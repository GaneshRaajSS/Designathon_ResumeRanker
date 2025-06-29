from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from db.Schema import JobDescriptionResponse, JobDescriptionCreate, RankingResponse
from .Service import create_job_description, get_job_descriptions_by_user
from docx import Document
from api.EmailNotification.report_service import generate_consultant_report
from api.Auth.okta_auth import require_role
from api.EmailNotification.Service import send_consultant_report_email
from datetime import datetime
import fitz, re
from api.Auth.okta_auth import get_current_user, require_role
from JDdb import SessionLocal
from sqlalchemy.orm import Session
from db.Model import EmailNotification, Ranking, JobDescription, ConsultantProfile, User, Application, SimilarityScore, WorkflowStatus
from typing import List
from enums import JobStatus, NotificationStatus, WorkflowStepStatus
from agents.ranking_service import init_or_update_workflow_status
from sqlalchemy import and_

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db  # Pass db to the route
    finally:
        db.close() 

#To See all JDs
@router.get("/job-descriptions", response_model=List[JobDescriptionResponse])
def get_all_job_descriptions(
    skip: int = 0,
    limit: int = 50,
):
    db: Session = SessionLocal()
    try:
        jds = (
            db.query(JobDescription)
            .order_by(JobDescription.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        if not jds:
            raise HTTPException(status_code=404, detail="No Job Descriptions found")

        return jds
    finally:
        db.close()

# # ✅ To See only pending JDs
@router.get("/job-descriptions/pending")
def get_pending_job_descriptions(user=Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        current_user = db.query(User).filter_by(email=user["sub"]).first()
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")

        pending_jds = (
            db.query(JobDescription)
            .filter(JobDescription.status == JobStatus.in_progress)
            .order_by(JobDescription.created_at.desc())
            .all()
        )

        return {
            "user_id": current_user.user_id,
            "pending_jobs": [
                {
                    "id": jd.id,
                    "title": jd.title,
                    "description": jd.description,
                    "skills": jd.skills,
                    "experience": jd.experience,
                    "status": jd.status,
                    "end_date": jd.end_date,
                }
                for jd in pending_jds
            ]
        }

    finally:
        db.close()


@router.get("/job-descriptions/{jd_id}/rankings", response_model=List[RankingResponse])
def get_rankings_for_jd(jd_id: str, db: Session = Depends(get_db)):
    jd = db.query(JobDescription).filter_by(id=jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")

    rankings = (
        db.query(Ranking)
        .filter(Ranking.jd_id == jd_id)
        .order_by(Ranking.rank.asc())
        .all()
    )

    if not rankings:
        raise HTTPException(status_code=404, detail="No rankings found for this JD")

    return rankings


#AR Requestor JD 
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

@router.get("/users/me/all-applied-jobs")
async def get_applied_jobs_for_logged_user(request: Request, user=Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        # Step 1: Get current user by email from token
        user_email = user.get("sub")
        current_user = db.query(User).filter_by(email=user_email).first()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Step 2: Get consultant profile(s) created by the user
        consultant_profiles = db.query(ConsultantProfile).filter_by(user_id=current_user.user_id).all()
        if not consultant_profiles:
            raise HTTPException(status_code=404, detail="No consultant profiles found for user")

        consultant_ids = [cp.id for cp in consultant_profiles]

        # Step 3: Get applications for those consultant profiles
        applications = db.query(Application).filter(Application.profile_id.in_(consultant_ids)).all()
        if not applications:
            return {"applied_jobs": []}

        jd_ids = [app.jd_id for app in applications]

        # Step 4: Fetch Job Descriptions
        jds = db.query(JobDescription).filter(JobDescription.id.in_(jd_ids)).all()

        # Step 5: Format response
        return {
            "user_id": current_user.user_id,
            "applied_jobs": [
                {
                    "id": jd.id,
                    "title": jd.title,
                    "description": jd.description,
                    "skills": jd.skills,
                    "experience": jd.experience,
                    "status": jd.status,
                    "end_date": jd.end_date,
                } for jd in jds
            ]
        }

    finally:
        db.close()

@router.get("/users/me/applied-jobs")
async def get_applied_jobs_for_logged_user(request: Request, user=Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        user_email = user.get("sub")
        current_user = db.query(User).filter_by(email=user_email).first()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        consultant_profiles = db.query(ConsultantProfile).filter_by(user_id=current_user.user_id).all()
        if not consultant_profiles:
            raise HTTPException(status_code=404, detail="No consultant profiles found for user")

        consultant_ids = [cp.id for cp in consultant_profiles]

        # Get all applications made by the user's consultant profiles
        applications = db.query(Application).filter(Application.profile_id.in_(consultant_ids)).all()
        if not applications:
            return {"user_id": current_user.user_id, "applied_jobs": []}

        jd_ids = [app.jd_id for app in applications]

        job_list = []
        for jd in db.query(JobDescription).filter(JobDescription.id.in_(jd_ids)).all():
            # Skip if status is 'completed' and user not in Ranking table for that JD
            if jd.status == JobStatus.completed:
                # Check if any consultant profile is ranked for this JD
                is_ranked = db.query(Ranking).filter(
                    and_(
                        Ranking.jd_id == jd.id,
                        Ranking.profile_id.in_(consultant_ids)
                    )
                ).first()
                if not is_ranked:
                    continue  # Skip this JD

            job_list.append({
                "id": jd.id,
                "title": jd.title,
                "description": jd.description,
                "skills": jd.skills,
                "experience": jd.experience,
                "status": jd.status,
                "end_date": jd.end_date,
            })

        return {
            "user_id": current_user.user_id,
            "applied_jobs": job_list
        }

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
        import traceback
        print("Upload Error:", traceback.format_exc())
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


@router.patch("/job-descriptions/{jd_id}/status")
def update_jd_status(jd_id: str, request: JobStatusUpdateRequest, user=Depends(require_role(["ARRequestor"]))):
    new_status = request.status
    db: Session = SessionLocal()
    try:
        jd = db.query(JobDescription).filter_by(id=jd_id).first()
        if not jd:
            raise HTTPException(status_code=404, detail="Job Description not found")

        jd.status = new_status

        db.commit()

        # ✅ Trigger email only if status set to 'Completed'
        if new_status == JobStatus.completed:
            print(f"JD {jd.id} marked as completed. Preparing to send email...")

            # Get top 3 consultants by rank
            rankings = db.query(Ranking).filter_by(jd_id=jd.id).order_by(Ranking.rank.asc()).limit(3).all()
            if not rankings:
                return {"message": "JD marked completed, but no consultant rankings found."}

            consultants = []
            for r in rankings:
                profile = db.query(ConsultantProfile).filter_by(id=r.profile_id).first()
                score_entry = db.query(SimilarityScore).filter_by(jd_id=jd.id, profile_id=r.profile_id).first()
                if profile:
                    consultants.append({
                        "consultant_id": profile.id,
                        "name": profile.name,
                        "email": profile.email,
                        "score": round(score_entry.similarity_score, 2) if score_entry else 0.0,
                        "explanation": r.explanation
                    })

            # Get JD owner (AR)
            ar_user = db.query(User).filter_by(user_id=jd.user_id).first()
            if not ar_user:
                raise HTTPException(status_code=404, detail="Associated user not found for JD")

            # Generate report and send email
            pdf_url = generate_consultant_report(jd.id, consultants, jd_obj=jd)
            status = send_consultant_report_email(ar_user.email, jd.id, pdf_url, db, consultants)

            # ✅ Always add new email notification entry
            db.add(EmailNotification(
                jd_id=jd.id,
                recipient_email=ar_user.email,
                status="Sent" if status.lower() == "sent" else "Failed",
                sent_at=datetime.utcnow()
            ))

            # ✅ Update WorkflowStatus (comparison, ranking, email)
            init_or_update_workflow_status(db, jd.id)
            workflow = db.query(WorkflowStatus).filter_by(jd_id=jd.id).first()
            if workflow:
                workflow.email_status = NotificationStatus.sent if status.lower() == "sent" else NotificationStatus.failed
            db.commit()

            return {"message": f"JD completed and consultant report email {'sent' if status.lower() == 'sent' else 'failed'}."}

        return {"message": f"JD status updated to {new_status}"}
    finally:
        db.close()
