# api/job_descriptions/schema.py
from pydantic import BaseModel, Field

class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    skills: str = Field(..., min_length=3)
    experience: str = Field(..., min_length=2)

class JobDescriptionResponse(JobDescriptionCreate):
    id: str
