# ✅ ROUTES FILE: api/JDProfileHistory/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.Schema import JDProfileHistoryResponse
from api.JDProfileHistory.Service import get_all_jd_profile_history_db, get_history_by_jd_db, get_db
from api.Auth.okta_auth import get_current_user

router = APIRouter()

@router.get("/jd-profile-history", response_model=list[JDProfileHistoryResponse])
def get_all_jd_profile_history(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_all_jd_profile_history_db(user, db)

@router.get("/jd/{jd_id}/history", response_model=list[JDProfileHistoryResponse])
def get_history_by_jd(jd_id: str, db: Session = Depends(get_db)):
    return get_history_by_jd_db(jd_id, db)
