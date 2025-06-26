# api/job_descriptions/service.py
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy.exc import SQLAlchemyError
from db.Model import JobDescription, WorkflowStatus,User, Ranking, ConsultantProfile, SimilarityScore,EmailNotification
from JDdb import SessionLocal
from api.EmailNotification.report_service import generate_consultant_report, generate_sas_url
from api.EmailNotification.Service import send_consultant_report_email
from agents.embedding_service import get_embedding
from enums import JobStatus, NotificationStatus
from sqlalchemy.orm import Session

async def create_job_description(data):
    db = SessionLocal()
    try:
        # ✅ Generate ID if not provided
        jd_id = data.get("id", str(uuid.uuid4()))

        # ✅ Check if JD with that ID exists
        existing_jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()

        text_for_embedding = data["title"] + "\n" + data["skills"] + "\n" + data["experience"]
        embedding = await get_embedding(text_for_embedding)

        status = data.get("status", JobStatus.in_progress)
        if isinstance(status, str):
            try:
                status = JobStatus(status)
            except ValueError:
                raise Exception(f"Invalid status value: {status}")

        if status == JobStatus.completed:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.utcnow().date() + timedelta(weeks=3)

        if existing_jd:
            existing_jd.title = data["title"]
            existing_jd.description = data["description"]
            existing_jd.skills = data["skills"]
            existing_jd.experience = data["experience"]
            existing_jd.status = status.value
            existing_jd.end_date = end_date
            existing_jd.embedding = embedding
            db.commit()
            db.refresh(existing_jd)
            return existing_jd

        # ✅ Create new JobDescription
        jd = JobDescription(
            id=jd_id,
            title=data["title"],
            description=data["description"],
            skills=data["skills"],
            experience=data["experience"],
            status=status.value,
            end_date=end_date,
            embedding=embedding,
            user_id=data["user_id"]
        )
        db.add(jd)
        db.flush()

        workflow = WorkflowStatus(
            jd_id=jd.id,
            comparison_status="Pending",
            ranking_status="Pending",
            email_status="Pending"
        )
        db.add(workflow)

        db.commit()
        db.refresh(jd)
        return jd

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating JD: {str(e)}")
    finally:
        db.close()


def get_job_descriptions_by_user(user_id: str):
    from JDdb import SessionLocal  # local import to avoid circular dependency
    db = SessionLocal()
    try:
        return db.query(JobDescription).filter(JobDescription.user_id == user_id).all()
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching JDs: {str(e)}")
    finally:
        db.close()


def mark_expired_jds_as_completed():
    db: Session = SessionLocal()
    try:
        today = date.today()
        print("🔍 Checking for expired Job Descriptions...")

        expired_jds = db.query(JobDescription).filter(
            JobDescription.status != JobStatus.completed,
            JobDescription.end_date < today
        ).all()

        print(f"🧾 Found {len(expired_jds)} expired JDs.")

        for jd in expired_jds:
            print(f"📌 Processing JD: {jd.id} - {jd.title}")
            jd.status = JobStatus.completed

            # Get JD owner
            user = db.query(User).filter(User.user_id == jd.user_id).first()
            if not user:
                print(f"⚠️ No user found for JD {jd.id}")
                continue

            # Get top 3 consultants
            rankings = db.query(Ranking).filter_by(jd_id=jd.id).order_by(Ranking.rank.asc()).limit(3).all()
            if not rankings:
                print(f"⚠️ No rankings found for JD {jd.id}")
                continue

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

            # Generate report
            pdf_url = generate_consultant_report(jd.id, consultants, jd_obj=jd)
            print(f"📄 PDF generated for JD {jd.id}: {pdf_url}")

            # Send email
            status = send_consultant_report_email(user.email, jd.id, pdf_url, db, consultants)
            print(f"📬 Email send status for JD {jd.id}: {status}")

            # Always add a new email record
            db.add(EmailNotification(
                jd_id=jd.id,
                recipient_email=user.email,
                status="Sent" if status.lower() == "sent" else "Failed",
                sent_at=datetime.utcnow()
            ))

            # Update WorkflowStatus
            workflow = db.query(WorkflowStatus).filter_by(jd_id=jd.id).first()
            if workflow:
                workflow.email_status = NotificationStatus.sent if status.lower() == "sent" else NotificationStatus.failed

        db.commit()
        print(f"✅ Completed processing {len(expired_jds)} expired JDs.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error in mark_expired_jds_as_completed: {str(e)}")
    finally:
        db.close()
