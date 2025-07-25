from JDdb import SessionLocal
from sqlalchemy.orm import Session
from db.Model import SimilarityScore, User, ConsultantProfile

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_jd_ids(user_email: str, db: Session) -> list[str]:
    user = db.query(User).filter_by(email=user_email).first()
    return [jd.id for jd in user.job_descriptions] if user else []

def get_all_similarity_scores_db(user: dict, db: Session):
    if user["role"] == "Recruiter":
        return db.query(SimilarityScore).all()
    jd_ids = get_user_jd_ids(user["sub"], db)
    return db.query(SimilarityScore).filter(SimilarityScore.jd_id.in_(jd_ids)).all()

def get_similarity_scores_by_jd_db(jd_id: str, db: Session):
    return (
        db.query(
            SimilarityScore.jd_id,
            SimilarityScore.profile_id,
            SimilarityScore.similarity_score.label("score"),
            SimilarityScore.similarity_id,
            SimilarityScore.created_at,
            User.name.label("name"),
            User.email.label("email"),
        )
        .join(ConsultantProfile, ConsultantProfile.id == SimilarityScore.profile_id)
        .join(User, User.user_id == ConsultantProfile.user_id)
        .filter(SimilarityScore.jd_id == jd_id)
        .order_by(SimilarityScore.similarity_score.desc())
        .limit(5)
        .all()
    )
