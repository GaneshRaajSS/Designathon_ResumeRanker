import uuid
import hashlib
import json
import re, os
from sqlalchemy.exc import SQLAlchemyError
from db.Model import ConsultantProfile
from JDdb import SessionLocal
from .Extractor import extract_sections
from agents.embedding_service import get_embedding
from azure.storage.blob import BlobServiceClient

def compute_resume_hash(sections: dict, resume_text: str) -> str:
    normalized_text = re.sub(r'\s+', ' ', resume_text.lower().strip()) if resume_text else ""
    relevant_data = {
        "skills": sections.get("skills"),
        "experience": sections.get("experience"),
        "projects": sections.get("projects"),
        "education": sections.get("education"),
        "resume_text": normalized_text.strip()
    }
    normalized = json.dumps(relevant_data, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()

def safe_value(parsed_val, fallback_val, min_len=3):
    return parsed_val if parsed_val and len(parsed_val.strip()) >= min_len else fallback_val or "Not specified"

# def create_consultant(data, skip_if_duplicate=True):
#     db = SessionLocal()
#     try:
#         resume_text = data.get("resume_text", "")
#         parsed = extract_sections(resume_text)
#         resume_hash = compute_resume_hash(parsed, resume_text)

#         # Look for existing consultant by email
#         existing = db.query(ConsultantProfile).filter_by(email=parsed.get("email")).first()

#         if existing:
#             if skip_if_duplicate and existing.content_hash == resume_hash:
#                 return existing, "duplicate"  # Resume unchanged
#             else:
#                 # Resume changed — update existing
#                 existing.name = parsed.get("name") or data.get("name")
#                 existing.skills = safe_value(parsed.get("skills"), data.get("skills"))
#                 existing.experience = safe_value(parsed.get("experience"), data.get("experience"))
#                 existing.resume_text = resume_text
#                 existing.content_hash = resume_hash

#                 db.commit()
#                 db.refresh(existing)
#                 return existing, "updated"

#         # New consultant case
#         consultant_id = str(uuid.uuid4())
#         consultant = ConsultantProfile(
#             id=consultant_id,
#             name=parsed.get("name") or data.get("name"),
#             email=parsed.get("email") or data.get("email"),
#             skills=safe_value(parsed.get("skills"), data.get("skills")),
#             experience=safe_value(parsed.get("experience"), data.get("experience")),
#             resume_text=resume_text,
#             content_hash=resume_hash
#         )

#         db.add(consultant)
#         db.commit()
#         db.refresh(consultant)
#         return consultant, "created"

#     except SQLAlchemyError as e:
#         db.rollback()
#         raise Exception(f"Database error while creating Consultant: {str(e)}")
#     finally:
#         db.close()

async def create_consultant(data, skip_if_duplicate=True):
    db = SessionLocal()
    try:
        resume_text = data.get("resume_text", "")
        parsed = await extract_sections(resume_text)
        resume_hash = compute_resume_hash(parsed, resume_text)

        # Check for existing by email
        existing = db.query(ConsultantProfile).filter_by(email=parsed.get("email")).first()

        # Text for embedding
        skills = safe_value(parsed.get("skills"), data.get("skills"))
        experience = safe_value(parsed.get("experience"), data.get("experience"))
        text_for_embedding = f"{skills}\n{experience}"

        if existing:
            if skip_if_duplicate and existing.content_hash == resume_hash:
                return existing, "duplicate"

            # Resume changed → update + re-embed
            existing.name = parsed.get("name") or data.get("name")
            existing.skills = skills
            existing.experience = experience
            existing.resume_text = resume_text
            existing.content_hash = resume_hash
            existing.embedding = await get_embedding(text_for_embedding)

            db.commit()
            db.refresh(existing)
            return existing, "updated"

        # New consultant
        consultant_id = str(uuid.uuid4())
        embedding = await get_embedding(text_for_embedding)
        consultant = ConsultantProfile(
            id=consultant_id,
            name=parsed.get("name") or data.get("name"),
            email=parsed.get("email") or data.get("email"),
            skills=skills,
            experience=experience,
            resume_text=resume_text,
            content_hash=resume_hash,
            embedding=embedding
        )
        db.add(consultant)
        db.commit()
        db.refresh(consultant)
        return consultant, "created"

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating/updating Consultant: {str(e)}")
    finally:
        db.close()

def get_consultant(consultant_id):
    db = SessionLocal()
    try:
        return db.query(ConsultantProfile).filter(ConsultantProfile.id == consultant_id).first()
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching Consultant: {str(e)}")
    finally:
        db.close()

#BLOB STORAGE
blob_service_client = BlobServiceClient.from_connection_string(
    f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};"
    f"AccountKey={os.getenv('AZURE_STORAGE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"
)
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

def upload_resume_to_blob(consultant_id: str, file_content: bytes):
    blob_path = f"resumes/{consultant_id}.pdf"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
    blob_client.upload_blob(file_content, overwrite=True)

def move_resume_to_jd_folder(consultant_id: str, jd_id: str):
    source_blob = f"resumes/{consultant_id}.pdf"
    dest_blob = f"JD/{jd_id}/{consultant_id}.pdf"

    source_blob_client = blob_service_client.get_blob_client(container=container_name, blob=source_blob)
    dest_blob_client = blob_service_client.get_blob_client(container=container_name, blob=dest_blob)

    # Copy source to destination
    copy_url = source_blob_client.url
    dest_blob_client.start_copy_from_url(copy_url)
