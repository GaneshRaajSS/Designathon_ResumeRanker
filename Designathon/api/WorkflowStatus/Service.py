from db.Model import WorkflowStatus,User
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

def get_all_workflows_db(user: dict, db: Session):
    if user["role"] == "Recruiter":
        return db.query(WorkflowStatus).all()
    jd_ids = get_user_jd_ids(user["sub"], db)
    return db.query(WorkflowStatus).filter(WorkflowStatus.jd_id.in_(jd_ids)).all()

def get_workflow_status_by_jd_db(jd_id: str, db: Session):
    return db.query(WorkflowStatus).filter_by(jd_id=jd_id).first()
