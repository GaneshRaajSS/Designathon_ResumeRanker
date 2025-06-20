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
