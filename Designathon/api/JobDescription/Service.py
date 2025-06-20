# api/job_descriptions/service.py
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy.exc import SQLAlchemyError
from db.Model import JobDescription, WorkflowStatus
from JDdb import SessionLocal
from agents.embedding_service import get_embedding
from enums import JobStatus
from sqlalchemy.orm import Session

async def create_job_description(data):
    db = SessionLocal()
    try:
        # ✅ Generate ID if not provided
        jd_id = data.get("id", str(uuid.uuid4()))

        # ✅ Check if JD with that ID exists
        existing_jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()

        text_for_embedding = data["title"] + "\n" + data["skills"] + "\n" + data["experience"]
        embedding = await get_embedding(text_for_embedding)

        status = data.get("status", JobStatus.in_progress)
        if isinstance(status, str):
            try:
                status = JobStatus(status)
            except ValueError:
                raise Exception(f"Invalid status value: {status}")

        if status == JobStatus.completed:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.utcnow().date() + timedelta(weeks=3)

        if existing_jd:
            existing_jd.title = data["title"]
            existing_jd.description = data["description"]
            existing_jd.skills = data["skills"]
            existing_jd.experience = data["experience"]
            existing_jd.status = status.value
            existing_jd.end_date = end_date
            existing_jd.embedding = embedding
            db.commit()
            db.refresh(existing_jd)
            return existing_jd

        # ✅ Create new JobDescription
        jd = JobDescription(
            id=jd_id,
            title=data["title"],
            description=data["description"],
            skills=data["skills"],
            experience=data["experience"],
            status=status.value,
            end_date=end_date,
            embedding=embedding,
            user_id=data["user_id"]
        )
        db.add(jd)
        db.flush()

        workflow = WorkflowStatus(
            jd_id=jd.id,
            comparison_status="Pending",
            ranking_status="Pending",
            email_status="Pending"
        )
        db.add(workflow)

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


def mark_expired_jds_as_completed():
    db: Session = SessionLocal()
    try:
        today = date.today()
        updated = db.query(JobDescription).filter(
            JobDescription.status != JobStatus.completed,
            JobDescription.end_date < today
        ).update({JobDescription.status: JobStatus.completed}, synchronize_session=False)
        db.commit()
        print(f"✅ Auto-completed {updated} expired job descriptions.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error marking expired JDs: {str(e)}")
    finally:
        db.close()
