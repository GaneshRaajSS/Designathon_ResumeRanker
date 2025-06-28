from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from db.Schema import ConsultantResponse
from .Service import create_consultant, get_consultant, upload_resume_to_blob
import fitz, os
from api.Auth.okta_auth import get_current_user, require_role
from JDdb import SessionLocal
from db.Model import User
from db.Model import ConsultantProfile
router = APIRouter()

@router.get("/consultants/{consultant_id}", response_model=ConsultantResponse)
def read_consultant(consultant_id: str, user=Depends(require_role(["Recruiter"]))):
    try:
        consultant = get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        return consultant
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/consultant/upload/")
async def upload_consultant_resume(file: UploadFile = File(...), user=Depends(require_role(["User"]))):
    try:
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        resume_text = "\n".join([page.get_text() for page in doc])

        db = SessionLocal()
        db_user = db.query(User).filter_by(email=user["sub"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        consultant, status = await create_consultant({
            "resume_text": resume_text,
            "user_id": db_user.user_id
        }, skip_if_duplicate=False)

        # ✅ Upload to blob with known ID (existing or new)
        upload_resume_to_blob(consultant.id, contents)

        return {
            "status": status,
            "consultant": {
                "id": consultant.id,
                "name": consultant.name,
                "email": consultant.email,
                "skills": consultant.skills,
                "experience": consultant.experience,
                "resume_text": consultant.resume_text,
                "user_id": consultant.user_id
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error Processing Resume: {str(e)}")
    finally:
        db.close()
