from db.Model import JDProfileHistory
from JDdb import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
import uuid

def create_history_entry(data, db):
    try:
        entry = JDProfileHistory(
            history_id=str(uuid.uuid4()),
            jd_id=data["jd_id"],
            profile_id=data["profile_id"],
            action=data["action"]
        )
        db.add(entry)
        print(f"📚 JD History saved for profile {data['profile_id']} with action {data['action']}")
        db.flush()
        return entry
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating history entry: {str(e)}")