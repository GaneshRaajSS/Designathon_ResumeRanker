from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from db.Schema import ConsultantResponse
from .Service import create_consultant, get_consultant, upload_resume_to_blob
import fitz, os
from api.Auth.okta_auth import get_current_user, require_role

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
# def read_consultant(consultant_id: str, token_data: dict = Depends(verify_token)):
#     try:
#         consultant = get_consultant(consultant_id)
#         if not consultant:
#             raise HTTPException(status_code=404, detail="Consultant not found")
#         return consultant
#     except Exception as e:
        # raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/consultant/upload/")
async def upload_consultant_resume(file: UploadFile = File(...), user=Depends(require_role(["Recruiter"]))):
    try:
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        resume_text = "\n".join([page.get_text() for page in doc])

        consultant, status = await create_consultant({"resume_text": resume_text})
        
        # Upload PDF to blob storage
        upload_resume_to_blob(consultant.id, contents)

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

# @router.post("/consultant/upload/")
# async def upload_consultant_resume(file: UploadFile = File(...)):
#     try:
#         contents = await file.read()
#         doc = fitz.open(stream=contents, filetype="pdf")
#         resume_text = "\n".join([page.get_text() for page in doc])

#         consultant, status = await create_consultant({"resume_text": resume_text})

#         return {
#             "status": status,
#             "consultant": {
#                 "id": consultant.id,
#                 "name": consultant.name,
#                 "email": consultant.email,
#                 "skills": consultant.skills,
#                 "experience": consultant.experience,
#                 "resume_text": consultant.resume_text
#             }
#         }

#     except Exception as e:
        # raise HTTPException(status_code=500, detail=f"Error Processing Resume: {str(e)}")
