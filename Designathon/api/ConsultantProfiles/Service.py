import uuid
import hashlib
import json
import re
from sqlalchemy.exc import SQLAlchemyError
from Model import ConsultantProfile
from JDdb import SessionLocal
from .Extractor import extract_sections

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

def create_consultant(data, skip_if_duplicate=True):
    db = SessionLocal()
    try:
        resume_text = data.get("resume_text", "")
        parsed = extract_sections(resume_text)
        resume_hash = compute_resume_hash(parsed, resume_text)

        # Look for existing consultant by email
        existing = db.query(ConsultantProfile).filter_by(email=parsed.get("email")).first()

        if existing:
            if skip_if_duplicate and existing.content_hash == resume_hash:
                return existing, "duplicate"  # Resume unchanged
            else:
                # Resume changed — update existing
                existing.name = parsed.get("name") or data.get("name")
                existing.skills = safe_value(parsed.get("skills"), data.get("skills"))
                existing.experience = safe_value(parsed.get("experience"), data.get("experience"))
                existing.resume_text = resume_text
                existing.content_hash = resume_hash

                db.commit()
                db.refresh(existing)
                return existing, "updated"

        # New consultant case
        consultant_id = str(uuid.uuid4())
        consultant = ConsultantProfile(
            id=consultant_id,
            name=parsed.get("name") or data.get("name"),
            email=parsed.get("email") or data.get("email"),
            skills=safe_value(parsed.get("skills"), data.get("skills")),
            experience=safe_value(parsed.get("experience"), data.get("experience")),
            resume_text=resume_text,
            content_hash=resume_hash
        )

        db.add(consultant)
        db.commit()
        db.refresh(consultant)
        return consultant, "created"

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating Consultant: {str(e)}")
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
