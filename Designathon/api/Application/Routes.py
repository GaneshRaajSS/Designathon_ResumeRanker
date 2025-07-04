from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from JDdb import SessionLocal
from db.Model import Application, Ranking, JobDescription, ConsultantProfile, User, SimilarityScore
from db.Schema import ApplicationCreate  # Schema with just jd_id
from agents.ranking_service import rank_profiles, finalize_and_notify
from api.ConsultantProfiles.Service import move_resume_to_jd_folder
from api.Auth.okta_auth import require_role, get_current_user
from skills import skill_lookup

router = APIRouter()

@router.post("/apply")
def apply_to_jd(
    application: ApplicationCreate, 
    background_tasks: BackgroundTasks,
    user=Depends(require_role(["User", "Recruiter"]))
):
    db: Session = SessionLocal()
    try:
        # Get consultant linked to this user
        user_record = db.query(User).filter_by(email=user["sub"]).first()
        if not user_record:
            raise HTTPException(status_code=401, detail="User not found")

        profile = db.query(ConsultantProfile).filter_by(user_id=user_record.user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Consultant profile not found")

        profile_id = profile.id
        jd_id = application.jd_id

        exists = db.query(Application).filter_by(jd_id=jd_id, profile_id=profile_id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Already applied to this JD")

        new_app = Application(jd_id=jd_id, profile_id=profile_id)
        db.add(new_app)
        db.commit()

        background_tasks.add_task(rank_consultant, jd_id, profile_id)

        return {"message": "Application submitted and ranking scheduled"}

    finally:
        db.close()

@router.get("/jobs")
def get_all_jobs(user=Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        jobs = db.query(JobDescription).all()
        return [
            {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "skills": job.skills,
                "experience": job.experience,
                "status": job.status,
                "end_date": job.end_date,
                "created_at": job.created_at,
                "posted_by": job.user.name if job.user else "Unknown"
            }
            for job in jobs
        ]
    finally:
        db.close()
        
@router.get("/job-descriptions/{jd_id}/applications")
def get_jd_applications(jd_id: str):
    db: Session = SessionLocal()

    # Join Ranking and ConsultantProfile to get rank along with consultant details
    results = (
        db.query(ConsultantProfile, Ranking.rank)
        .join(Ranking, Ranking.profile_id == ConsultantProfile.id)
        .filter(Ranking.jd_id == jd_id)
        .order_by(Ranking.rank.asc())
        .all()
    )

    return [
        {
            "id": profile.id,
            "name": profile.name,
            "email": profile.email,
            "skills": profile.skills,
            "experience": profile.experience,
            "rank": rank
        }
        for profile, rank in results
    ]

def calculate_skill_match(
    jd_skills: str, 
    profile_skills: str, 
    skill_lookup: dict
) -> tuple[float, list[str]]:
    def normalize(skills: str) -> set[str]:
        return {
            skill_lookup.get(skill.strip().lower(), skill.strip().lower())
            for skill in skills.split(',') if skill.strip()
        }

    jd_skill_set = normalize(jd_skills)
    profile_skill_set = normalize(profile_skills)

    if not jd_skill_set:
        return 1.0, []

    matched = jd_skill_set & profile_skill_set
    missing = jd_skill_set - profile_skill_set
    match_ratio = len(matched) / len(jd_skill_set)

    return round(match_ratio, 2), sorted(missing)


async def rank_consultant(jd_id: str, profile_id: str):
    db: Session = SessionLocal()
    try:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        profile = db.query(ConsultantProfile).filter_by(id=profile_id).first()
        if not jd or not profile:
            return
        
        # 🚫 Reject if experience is insufficient
        if profile.experience < jd.experience:
            print(f"❌ Rejected: {profile.name} has {profile.experience} years, needs {jd.experience}")
            return

        # 🚫 Reject if skills match is less than 50%
        from agents.similarity_service import compute_cosine_similarity
        skill_match_ratio, missing_skills = calculate_skill_match(jd.skills, profile.skills, skill_lookup)
        if skill_match_ratio < 0.5:
            print(f"❌ Rejected: {profile.name} has insufficient skill match ({skill_match_ratio:.2%})")
            print(f"🔍 Missing Skills: {', '.join(missing_skills)}")
            return
        
         # 🚫 Don't recompute similarity score if it already exists
        existing_score = db.query(SimilarityScore).filter_by(
            jd_id=jd_id, profile_id=profile_id
        ).first()

        if not existing_score:
            from agents.similarity_service import  compute_cosine_similarity
            score = compute_cosine_similarity(jd.embedding, [profile.embedding])[0]
            db.add(SimilarityScore(
                jd_id=jd_id,
                profile_id=profile_id,
                similarity_score=score
            ))
            db.commit()
            print(f"🧠 Similarity saved: {profile.name} — {score:.4f}")
        else:
            print(f"✅ Similarity already exists for {profile.name}, skipping.")
        # Get ALL profiles that applied to this JD
        applications = db.query(Application).filter_by(jd_id=jd_id).all()
        profile_ids = [app.profile_id for app in applications]
        profiles = db.query(ConsultantProfile).filter(ConsultantProfile.id.in_(profile_ids)).all()

        if not profiles:
            return

        await rank_profiles(jd, profiles)
    finally:
        db.close()

