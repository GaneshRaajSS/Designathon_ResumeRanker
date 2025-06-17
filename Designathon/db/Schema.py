from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional,List
from enums import JobStatus, NotificationStatus, UserRoleStatus, WorkflowStepStatus, HistoryStatus, Enum
# schemas/user.py
# class UserCreate(BaseModel):
#     name: str
#     email: EmailStr
#     role: UserRoleStatus
#     okta_id: Optional[str] = None

# class UserResponse(UserCreate):
#     user_id: str
#     name: str
#     email: str
#     role: str
#     okta_id: Optional[str]
#     created_at: datetime

#     class Config:
#         from_attributes = True

class UserRoleStatus(str, Enum):
    admin = "admin"
    user = "user"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: UserRoleStatus

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# schemas/similarity_score.py
class SimilarityScoreCreate(BaseModel):
    jd_id: str
    profile_id: str
    similarity_score: float

class SimilarityScoreResponse(SimilarityScoreCreate):
    similarity_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# schemas/ranking.py
class RankingCreate(BaseModel):
    jd_id: str
    profile_id: str
    rank: int

class RankingResponse(RankingCreate):
    ranking_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# schemas/email_notification.py
class EmailNotificationCreate(BaseModel):
    jd_id: str
    recipient_email: EmailStr

class EmailNotificationResponse(EmailNotificationCreate):
    email_id: str
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


# schemas/workflow_status.py
class WorkflowStatusCreate(BaseModel):
    jd_id: str
    comparison_status: WorkflowStepStatus
    ranking_status: WorkflowStepStatus
    email_status: WorkflowStepStatus

class WorkflowStatusResponse(WorkflowStatusCreate):
    workflow_id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# schemas/ConsultantProfiles.py
class ConsultantCreate(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    skills: str = Field(..., min_length=3)
    experience: str = Field(..., min_length=2)
    embedding: Optional[List[float]] = None
    resume_text: Optional[str] = None
    availability: Optional[bool] = None

class ConsultantResponse(ConsultantCreate):
    id: str

    class Config:
        from_attributes = True


# schemas/JD.py
class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    skills: str = Field(..., min_length=3)
    experience: str = Field(..., min_length=2)
    status: JobStatus

class JobDescriptionResponse(JobDescriptionCreate):
    id: str
    # user_id: str
    embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# schemas/JDProfileHistory.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JDProfileHistoryCreate(BaseModel):
    jd_id: str = Field(...)
    profile_id: str = Field(...)
    # action: str = Field(..., example="shortlisted")
    action: HistoryStatus

class JDProfileHistoryResponse(JDProfileHistoryCreate):
    history_id: str
    created_at: datetime

    class Config:
        from_attributes = True