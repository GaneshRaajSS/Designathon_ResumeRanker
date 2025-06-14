from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from db.Schema import ConsultantCreate, ConsultantResponse
from .Service import create_consultant, get_consultant
import fitz


router = APIRouter()

@router.get("/consultants/{consultant_id}", response_model=ConsultantResponse)
def read_consultant(consultant_id: str):
    try:
        consultant = get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        return consultant
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/consultant/upload/")
async def upload_consultant_resume(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        resume_text = "\n".join([page.get_text() for page in doc])

        consultant, status = await create_consultant({"resume_text": resume_text})

        return {
            "status": status,
            "consultant": {
                "id": consultant.id,
                "name": consultant.name,
                "email": consultant.email,
                "skills": consultant.skills,
                "experience": consultant.experience,
                "resume_text": consultant.resume_text
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Processing Resume: {str(e)}")
