# ✅ ROUTES FILE: api/SimilarityScore/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.Schema import SimilarityScoreResponse
from api.SimilarityScore.Service import get_all_similarity_scores_db, get_similarity_scores_by_jd_db, get_db
from api.Auth.okta_auth import get_current_user

router = APIRouter()

@router.get("/similarity-scores", response_model=list[SimilarityScoreResponse])
def get_all_similarity_scores(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_all_similarity_scores_db(user, db)

@router.get("/jd/{jd_id}/similarity-scores", response_model=list[SimilarityScoreResponse])
def get_similarity_scores_by_jd(jd_id: str, db: Session = Depends(get_db)):
    return get_similarity_scores_by_jd_db(jd_id, db)
