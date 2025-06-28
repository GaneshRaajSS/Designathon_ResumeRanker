from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from JDdb import Base
import uuid
from enums import UserRoleStatus
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(50), default= UserRoleStatus.User, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_descriptions = relationship("JobDescription", back_populates="user")
    consultant_profiles = relationship("ConsultantProfile", back_populates="user")

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    skills = Column(Text, nullable=False)
    experience = Column(String(50), nullable=False)
    status = Column(String(50), default="In Progress")
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    user = relationship("User", back_populates="job_descriptions")
    similarity_scores = relationship("SimilarityScore", back_populates="job_description")
    rankings = relationship("Ranking", back_populates="job_description")
    emails = relationship("EmailNotification", back_populates="job_description")
    workflow_status = relationship("WorkflowStatus", uselist=False, back_populates="job_description")
    applications = relationship("Application", back_populates="job_description")


class ConsultantProfile(Base):
    __tablename__ = "consultant_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(100),  unique=True, nullable=False)
    skills = Column(Text, nullable=False)
    experience = Column(String(64), nullable=False)
    resume_text = Column(Text)
    availability = Column(Boolean, default=True)
    content_hash = Column(String(64))
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    user = relationship("User")

    similarity_scores = relationship("SimilarityScore", back_populates="consultant_profile")
    rankings = relationship("Ranking", back_populates="consultant_profile")
    
    applications = relationship("Application", back_populates="consultant_profile")

class SimilarityScore(Base):
    __tablename__ = "similarity_scores"

    similarity_id = Column(String(36), primary_key=True, default=generate_uuid)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    profile_id = Column(String(36), ForeignKey("consultant_profiles.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_description = relationship("JobDescription", back_populates="similarity_scores")
    consultant_profile = relationship("ConsultantProfile", back_populates="similarity_scores")


class Ranking(Base):
    __tablename__ = "rankings"

    ranking_id = Column(String(36), primary_key=True, default=generate_uuid)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    profile_id = Column(String(36), ForeignKey("consultant_profiles.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_description = relationship("JobDescription", back_populates="rankings")
    consultant_profile = relationship("ConsultantProfile", back_populates="rankings")

class EmailNotification(Base):
    __tablename__ = "email_notifications"

    email_id = Column(String(36), primary_key=True, default=generate_uuid)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    recipient_email = Column(String(100), nullable=False)
    status = Column(String(20), default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)

    job_description = relationship("JobDescription", back_populates="emails")


class WorkflowStatus(Base):
    __tablename__ = "workflow_statuses"

    workflow_id = Column(String(36), primary_key=True, default=generate_uuid)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id"), unique=True, nullable=False)
    comparison_status = Column(String(50), default="Pending")
    ranking_status = Column(String(50), default="Pending")
    email_status = Column(String(50), default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    job_description = relationship("JobDescription", back_populates="workflow_status")


class JDProfileHistory(Base):
    __tablename__ = "jd_profile_history"

    history_id = Column(String(36), primary_key=True, default=generate_uuid)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    profile_id = Column(String(36), ForeignKey("consultant_profiles.id"), nullable=False)
    action = Column(String(50), nullable=False, default="shortlisted")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_description = relationship("JobDescription")
    consultant_profile = relationship("ConsultantProfile")


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(String(36), primary_key = True, default=generate_uuid)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    profile_id = Column(String(36), ForeignKey("consultant_profiles.id"), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    job_description = relationship("JobDescription", back_populates="applications")
    consultant_profile = relationship("ConsultantProfile", back_populates="applications")   
    __table_args__ = (
        UniqueConstraint("jd_id", "profile_id", name="uq_application_once_per_jd"),
    )
