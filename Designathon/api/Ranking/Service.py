from db.Model import Ranking, User
from JDdb import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_jd_ids(user_email: str, db: Session) -> list[str]:
    user = db.query(User).filter_by(email=user_email).first()
    return [jd.id for jd in user.job_descriptions] if user else []

def get_all_rankings_db(user: dict, db: Session):
    if user["role"] == "Recruiter":
        return db.query(Ranking).all()
    jd_ids = get_user_jd_ids(user["sub"], db)
    return db.query(Ranking).filter(Ranking.jd_id.in_(jd_ids)).all()

def get_rankings_by_jd_db(jd_id: str, db: Session):
    return db.query(Ranking).filter_by(jd_id=jd_id).all()