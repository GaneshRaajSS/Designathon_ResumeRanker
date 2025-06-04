# api/job_descriptions/routes.py
from fastapi import APIRouter, HTTPException
from .Schema import JobDescriptionCreate, JobDescriptionResponse
from .Service import create_job_description, get_job_description

router = APIRouter()

@router.post("/job-descriptions/", response_model=JobDescriptionResponse)
def create_jd(jd: JobDescriptionCreate):
    try:
        created_jd = create_job_description(jd.dict())
        return created_jd
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
def read_jd(jd_id: str):
    try:
        jd = get_job_description(jd_id)
        if not jd:
            raise HTTPException(status_code=404, detail="Job Description not found")
        return jd
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
