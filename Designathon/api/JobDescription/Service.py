# api/job_descriptions/service.py
import uuid
from sqlalchemy.exc import SQLAlchemyError
from Model import JobDescription
from JDdb import SessionLocal

def create_job_description(data):
    db = SessionLocal()
    try:
        jd_id = str(uuid.uuid4())
        jd = JobDescription(id=jd_id, **data)
        db.add(jd)
        db.commit()
        db.refresh(jd)
        return jd
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating JD: {str(e)}")
    finally:
        db.close()

def get_job_description(jd_id):
    db = SessionLocal()
    try:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        return jd
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching JD: {str(e)}")
    finally:
        db.close()
