# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from sqlalchemy.orm import Session
# from JDdb import SessionLocal
# from db.Model import Application, Ranking, JobDescription, ConsultantProfile
# from db.Schema import ApplicationCreate
# from agents.ranking_service import rank_profiles, finalize_and_notify
# from api.ConsultantProfiles.Service import move_resume_to_jd_folder
# from api.Auth.okta_auth import require_role ,Depends

# router = APIRouter()

# @router.post("/apply")
# def apply_to_jd(application: ApplicationCreate, background_tasks: BackgroundTasks, user=Depends(require_role(["User", "Recruiter"]))):
#     db: Session = SessionLocal()
#     try:
#         exists = db.query(Application).filter_by(
#             jd_id=application.jd_id, profile_id=application.profile_id
#         ).first()
#         if exists:
#             raise HTTPException(status_code=400, detail="Already applied to this JD")

#         new_app = Application(
#             jd_id=application.jd_id,
#             profile_id=application.profile_id
#         )
#         db.add(new_app)
#         db.commit()

#         background_tasks.add_task(rank_consultant, application.jd_id, application.profile_id)

#         return {"message": "Application submitted and ranking scheduled"}
#     finally:
#         db.close()

# async def rank_consultant(jd_id: str, profile_id: str):
#     db: Session = SessionLocal()
#     try:
#         jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
#         profile = db.query(ConsultantProfile).filter(ConsultantProfile.id == profile_id).first()
#         if not jd or not profile:
#             return

#         result = await rank_profiles(jd, [profile])
#         await move_resume_to_jd_folder(profile.id, jd.id)
#         await finalize_and_notify(jd_id, result)
#     finally:
#         db.close()
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from JDdb import SessionLocal
from db.Model import Application, Ranking, JobDescription, ConsultantProfile, User
from db.Schema import ApplicationCreate  # Schema with just jd_id
from agents.ranking_service import rank_profiles, finalize_and_notify
from api.ConsultantProfiles.Service import move_resume_to_jd_folder
from api.Auth.okta_auth import require_role

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
