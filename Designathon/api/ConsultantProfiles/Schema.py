from pydantic import BaseModel, Field
from typing import Optional

class ConsultantCreate(BaseModel):
    name: str = Field(..., min_length=3)
    email: str = Field(..., pattern=r'^\S+@\S+\.\S+$')
    skills: str = Field(..., min_length=3)
    experience: str = Field(..., min_length=2)
    resume_text: str | None = None

class ConsultantResponse(ConsultantCreate):
    id: str
