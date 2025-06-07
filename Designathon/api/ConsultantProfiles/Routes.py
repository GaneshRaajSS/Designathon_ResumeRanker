from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from .Schema import ConsultantCreate, ConsultantResponse
from .Service import create_consultant, get_consultant
import fitz

router = APIRouter()

@router.post("/consultants/", response_model=ConsultantResponse)
def create_consultant_profile(profile: ConsultantCreate):
    try:
        created = create_consultant(profile.dict())
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/consultants/{consultant_id}", response_model=ConsultantResponse)
def read_consultant(consultant_id: str):
    try:
        consultant = get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        return consultant
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/consultant/upload/", response_model = ConsultantResponse)
async def upload_consultant_resume(
    file: UploadFile = File(...),
):
    try:
        contents = await file.read()
        doc = fitz.open(stream=contents,filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])

        created = create_consultant({
            "name": "",
            "email": "",
            "skills": "",
            "experience": "",
            "resume_text": text
        }, skip_if_duplicate=True)

        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Processing Resume: {str(e)}")
