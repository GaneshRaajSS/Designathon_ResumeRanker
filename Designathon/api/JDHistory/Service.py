from db.Model import JDProfileHistory
from JDdb import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
import uuid

def create_history_entry(data):
    db = SessionLocal()
    try:
        entry = JDProfileHistory(
            history_id=str(uuid.uuid4()),
            jd_id=data["jd_id"],
            profile_id=data["profile_id"],
            action=data["action"]
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating history entry: {str(e)}")
    finally:
        db.close()