# ✅ ROUTES FILE: api/Ranking/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.Schema import RankingResponse
from api.Ranking.Service import get_all_rankings_db, get_rankings_by_jd_db, get_db
from api.Auth.okta_auth import get_current_user

router = APIRouter()

@router.get("/rankings", response_model=list[RankingResponse])
def get_all_rankings(user=Depends(get_current_user), db: Session = Depends(get_db)):
    data = get_all_rankings_db(user, db)
    return data

@router.get("/jd/{jd_id}/rankings", response_model=list[RankingResponse])
def get_rankings_by_jd(jd_id: str, db: Session = Depends(get_db)):
    return get_rankings_by_jd_db(jd_id, db)
