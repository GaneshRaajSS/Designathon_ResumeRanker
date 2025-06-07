import uuid
from sqlalchemy.exc import SQLAlchemyError
from .Model import ConsultantProfile
from JDdb import SessionLocal
from .Extractor import extract_sections
import hashlib
import json

def safe_value(parsed_val, fallback_val, min_len=3):
    return parsed_val if parsed_val and len(parsed_val.strip()) >= min_len else fallback_val or "Not specified"

def create_consultant(data):
    db = SessionLocal()
    try:
        if data.get("resume_text"):
            parsed = extract_sections(data.get("resume_text"))
            name = parsed.get("name") or data.get("name")
            email = parsed.get("email") or data.get("email")
            skills = safe_value(parsed.get("skills"), data.get("skills"))
            experience = safe_value(parsed.get("experience"), data.get("experience"))
        else:
            name = data.get("name")
            email = data.get("email")
            skills = data.get("skills")
            experience = data.get("experience")

        consultant_id = str(uuid.uuid4())
        consultant = ConsultantProfile(
            id=consultant_id,
            name=name,
            email=email,
            skills=skills,
            experience=experience,
            resume_text=data.get("resume_text")
        )
        db.add(consultant)
        db.commit()
        db.refresh(consultant)
        return consultant
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating Consultant: {str(e)}")
    finally:
        db.close()


def get_consultant(consultant_id):
    db = SessionLocal()
    try:
        consultant = db.query(ConsultantProfile).filter(ConsultantProfile.id == consultant_id).first()
        return consultant
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching Consultant: {str(e)}")
    finally:
        db.close()

def compute_resume_hash(sections: dict) -> str:
    relevant_data = {
    "skills": sections.get("skills"),
    "experience": sections.get("experience"),
    "projects": sections.get("projects"),
    "education": sections.get("education")
    }
    normalized = json.dumps(relevant_data, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()

def create_consultant(data, skip_if_duplicate=True):
    db = SessionLocal()
    try:
        parsed = extract_sections(data.get("resume_text", ""))
        resume_hash = compute_resume_hash(parsed)

        if skip_if_duplicate:
            existing = db.query(ConsultantProfile).filter_by(email=parsed.get("email")).first()
            if existing and existing.content_hash == resume_hash:
                return existing

        consultant_id = str(uuid.uuid4())
        consultant = ConsultantProfile(
            id=consultant_id,
            name=parsed.get("name") or data.get("name"),
            email=parsed.get("email") or data.get("email"),
            skills=safe_value(parsed.get("skills"), data.get("skills")),
            experience=safe_value(parsed.get("experience"), data.get("experience")),
            resume_text=data.get("resume_text"),
            content_hash=resume_hash
        )

        db.add(consultant)
        db.commit()
        db.refresh(consultant)
        return consultant

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating Consultant: {str(e)}")
    finally:
        db.close()