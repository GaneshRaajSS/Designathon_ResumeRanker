# ✅ ROUTES FILE: api/EmailNotification/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.Schema import EmailNotificationResponse
from api.EmailNotification.Service import get_all_emails_db, get_emails_by_jd_db, get_db
from api.Auth.okta_auth import get_current_user

router = APIRouter()

@router.get("/emails", response_model=list[EmailNotificationResponse])
def get_all_emails(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_all_emails_db(user, db)

@router.get("/jd/{jd_id}/emails", response_model=list[EmailNotificationResponse])
def get_emails_by_jd(jd_id: str, db: Session = Depends(get_db)):
    return get_emails_by_jd_db(jd_id, db)

# api/EmailNotification/routes.py

from fastapi import APIRouter, Depends, HTTPException
from api.Auth.okta_auth import require_role
from api.EmailNotification.Service import send_email_with_consultant_report
from JDdb import SessionLocal
from db.Model import ConsultantProfile

router = APIRouter()

@router.post("/send-report-by-consultant/{profile_id}")
def send_report_by_consultant(
    profile_id: str,
    user=Depends(require_role(["Recruiter"]))  # ✅ Only Recruiters
):
    db = SessionLocal()
    profile = db.query(ConsultantProfile).filter_by(id=profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Consultant not found")

    send_email_with_consultant_report(profile_id, user["sub"])
    return {"message": f"Consultant match report sent to {user['sub']}"}

