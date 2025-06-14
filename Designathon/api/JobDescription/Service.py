# api/job_descriptions/service.py
import uuid
from sqlalchemy.exc import SQLAlchemyError
from db.Model import JobDescription
from JDdb import SessionLocal
from agents.embedding_service import get_embedding
# def create_job_description(data):
#     db = SessionLocal()
#     try:
#         jd_id = str(uuid.uuid4())
#         jd = JobDescription(id=jd_id, **data)
#         db.add(jd)
#         db.commit()
#         db.refresh(jd)
#         return jd
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise Exception(f"Database error while creating JD: {str(e)}")
#     finally:
#         db.close()

# async def create_job_description(data):
#     db = SessionLocal()
#     try:
#         # jd = db.query(JobDescription).filter(JobDescription.id == data["id"]).first()
#         jd = data.get("id", str(uuid.uuid4()))
#         text_for_embedding = data["title"] + "\n" + data["skills"] + "\n" + data["experience"]
#         embedding = await get_embedding(text_for_embedding)
#         if jd:
#             jd.title = data["title"]
#             jd.description = data["description"]
#             jd.skills = data["skills"]
#             jd.experience = data["experience"]
#             jd.embedding = embedding
#         else:
#             jd = JobDescription(
#                 id=data["id"],
#                 title=data["title"],
#                 description=data["description"],
#                 skills=data["skills"],
#                 experience=data["experience"],
#                 embedding=embedding
#             )
#             db.add(jd)
#         db.commit()
#         db.refresh(jd)
#         return jd
#     finally:
#         db.close()

import uuid
from sqlalchemy.exc import SQLAlchemyError
from db.Model import JobDescription
from JDdb import SessionLocal
from agents.embedding_service import get_embedding


async def create_job_description(data):
    db = SessionLocal()
    try:
        # ✅ Generate ID if not provided
        jd_id = data.get("id", str(uuid.uuid4()))

        # ✅ Check if JD with that ID exists
        existing_jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()

        text_for_embedding = data["title"] + "\n" + data["skills"] + "\n" + data["experience"]
        embedding = await get_embedding(text_for_embedding)

        if existing_jd:
            existing_jd.title = data["title"]
            existing_jd.description = data["description"]
            existing_jd.skills = data["skills"]
            existing_jd.experience = data["experience"]
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
            embedding=embedding
        )
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
