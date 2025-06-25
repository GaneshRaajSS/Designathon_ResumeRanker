from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from db.Schema import JobDescriptionResponse, JobDescriptionCreate
from .Service import create_job_description, get_job_descriptions_by_user
from docx import Document
import fitz, re
from api.Auth.okta_auth import get_current_user, require_role
from JDdb import SessionLocal
from db.Model import User
from typing import List

router = APIRouter()


# @router.get("/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
# def read_jd( jd_id: str, user=Depends(require_role(["ARRequestor"]))):
#     db = SessionLocal()
#     try:
#         # ✅ Get current user ID by their email from JWT
#         current_user = db.query(User).filter_by(email=user["sub"]).first()
#         if not current_user:
#             raise HTTPException(status_code=401, detail="User not found")

#         jd = get_job_description(jd_id)
#         if not jd:
#             raise HTTPException(status_code=404, detail="Job Description not found")

#         # ✅ Check if this JD was created by the logged-in user
#         if str(jd.user_id) != str(current_user.user_id):
#             return {
#                 "error": "Access denied",
#                 "jd_user_id": jd.user_id,
#                 "current_user_user_id": current_user.user_id,
#                 "jwt_email": user["sub"]
#             }
#         return jd

#     finally:
#         db.close()
@router.get("/job-descriptions/me", response_model=List[JobDescriptionResponse])
def get_my_job_descriptions(user=Depends(require_role(["ARRequestor"]))):
    db = SessionLocal()
    try:
        current_user = db.query(User).filter_by(email=user["sub"]).first()
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")

        return get_job_descriptions_by_user(current_user.user_id)

    finally:
        db.close()


def extract_text_from_pdf(file: UploadFile) -> str:
    doc = fitz.open(stream=file.file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])


def extract_text_from_docx(file: UploadFile) -> str:
    document = Document(file.file)
    return "\n".join([para.text for para in document.paragraphs])

def clean(text):
    return text.lstrip(":").strip()
def parse_jd_fields(text: str) -> dict:
    def extract_section(start_label, next_label=None):
        pattern = rf"{start_label}[:\-]?\s*(.*?)(?=\n\s*{next_label}[:\-]|\Z)" if next_label else rf"{start_label}[:\-]?\s*(.*)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    title = extract_section("Title", "Description")
    description = extract_section("Description", "Skills")
    skills = extract_section("Skills", "Experience")
    experience = extract_section("Experience")

    return {
    "title": clean(title),
    "description": description.strip(),
    "skills": clean(skills),
    "experience": clean(experience)
}


@router.post("/job-descriptions/upload", response_model=JobDescriptionResponse)
async def upload_jd_file(file: UploadFile = File(...), user=Depends(require_role(["ARRequestor"]))):
    db = SessionLocal()
    try:
        if file.filename.endswith(".pdf"):
            content = extract_text_from_pdf(file)
        elif file.filename.endswith(".docx"):
            content = extract_text_from_docx(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # parse fields from document
        parsed_fields = parse_jd_fields(content)

        # Validate required fields
        if not parsed_fields["title"] or not parsed_fields["skills"] or not parsed_fields["experience"]:
            raise HTTPException(status_code=400, detail="Missing required JD fields in document.")

        current_user = db.query(User).filter_by(email=user["sub"]).first()
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")
        parsed_fields["user_id"] = current_user.user_id

        jd = await create_job_description(parsed_fields)
        return JobDescriptionResponse.from_orm(jd)
        # return await create_job_description(parsed_fields)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()



@router.post("/job-descriptions/extract", response_model=JobDescriptionCreate)
async def extract_jd_fields(file: UploadFile = File(...), user=Depends(require_role(["ARRequestor"]))):
    try:
        if file.filename.endswith(".pdf"):
            content = extract_text_from_pdf(file)
        elif file.filename.endswith(".docx"):
            content = extract_text_from_docx(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        parsed_fields = parse_jd_fields(content)

        # Fallbacks to satisfy validation
        parsed_fields["title"] = parsed_fields.get("title") or "Untitled Role"
        parsed_fields["description"] = parsed_fields.get("description") or "No description provided"
        parsed_fields["skills"] = parsed_fields.get("skills") or "Not specified"
        parsed_fields["experience"] = parsed_fields.get("experience") or "0 years"

        return JobDescriptionCreate(**parsed_fields)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Step 2: Save user-edited JD data to DB
@router.post("/job-descriptions/submit", response_model=JobDescriptionResponse)
async def submit_jd(jd_data: JobDescriptionCreate, user=Depends(require_role(["ARRequestor"]))):
    db = SessionLocal()
    try:
        current_user = db.query(User).filter_by(email=user["sub"]).first()
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")
        # Inject user_id into jd_data
        jd_dict = jd_data.dict()
        jd_dict["user_id"] = current_user.user_id
        return await create_job_description(jd_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

