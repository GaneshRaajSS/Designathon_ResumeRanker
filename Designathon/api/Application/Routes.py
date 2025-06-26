from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from JDdb import SessionLocal
from db.Model import Application, Ranking, JobDescription, ConsultantProfile, User
from db.Schema import ApplicationCreate  # Schema with just jd_id
from agents.ranking_service import rank_profiles, finalize_and_notify
from api.ConsultantProfiles.Service import move_resume_to_jd_folder
from api.Auth.okta_auth import require_role, get_current_user

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

async def rank_consultant(jd_id: str, profile_id: str):
    db: Session = SessionLocal()
    try:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        profile = db.query(ConsultantProfile).filter(ConsultantProfile.id == profile_id).first()
        if not jd or not profile:
            return

        result = await rank_profiles(jd, [profile])
        await move_resume_to_jd_folder(profile.id, jd.id)
        await finalize_and_notify(jd_id, result)
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
