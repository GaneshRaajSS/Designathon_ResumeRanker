from db.Model import EmailNotification, User, WorkflowStatus, JobDescription, Ranking,ConsultantProfile
from JDdb import SessionLocal
from sqlalchemy.orm import Session, joinedload
from azure.communication.email import EmailClient
import os, base64, requests, asyncio
from datetime import datetime, date
from enums import WorkflowStepStatus, NotificationStatus
import time
from api.EmailNotification.report_service import generate_pdf_report_by_consultant
from api.EmailNotification.report_service import generate_sas_url


MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_jd_ids(user_email: str, db: Session) -> list[str]:
    user = db.query(User).filter_by(email=user_email).first()
    return [jd.id for jd in user.job_descriptions] if user else []

def get_all_emails_db(user: dict, db: Session):
    if user["role"] == "Recruiter":
        return db.query(EmailNotification).all()
    jd_ids = get_user_jd_ids(user["sub"], db)
    return db.query(EmailNotification).filter(EmailNotification.jd_id.in_(jd_ids)).all()

def get_emails_by_jd_db(jd_id: str, db: Session):
    return db.query(EmailNotification).filter_by(jd_id=jd_id).all()

def send_consultant_report_email(to_email: str, jd_id: str, pdf_url: str, db: Session, consultants: list[dict]) -> str:
    connection_string = os.getenv("AZURE_COMM_EMAIL_CONNECTION_STRING")
    sender = os.getenv("EMAIL_SENDER_ADDRESS")

    # Load PDF from URL
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        file_bytes = response.content
        encoded_file = base64.b64encode(file_bytes).decode("utf-8")
    except Exception as e:
        _record_email_failure(db, jd_id, to_email, f"PDF download failed: {str(e)}")
        raise Exception(f"Failed to download PDF: {str(e)}")

    # Fetch JD from DB
    jd = db.query(JobDescription).filter_by(id=jd_id).first()
    if not jd:
        raise Exception("JD not found for email report.")

    # Generate SAS links for resumes
    sas_resume_links = {
        c["consultant_id"]: generate_sas_url(f"JD/{jd_id}/{c['consultant_id']}.pdf")
        for c in consultants
    }

    # Build HTML email body like Swiggy style
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #fa541c;">Your Consultant Ranking Report is Ready</h2>

        <p>Greetings,</p>
        <p>The ranking for your Job Description <strong>{jd.title}</strong> is complete. Please find the report attached and summary below.</p>

        <h3 style="color: #1890ff;">Job Description Summary</h3>
        <table cellpadding="6" cellspacing="0" border="0">
          <tr><td><strong>JD ID:</strong></td><td>{jd_id}</td></tr>
          <tr><td><strong>Title:</strong></td><td>{jd.title}</td></tr>
          <tr><td><strong>Skills:</strong></td><td>{jd.skills}</td></tr>
          <tr><td><strong>Experience:</strong></td><td>{jd.experience}</td></tr>
          <tr><td><strong>End Date:</strong></td><td>{jd.end_date.strftime('%Y-%m-%d')}</td></tr>
        </table>

        <h3 style="color: #1890ff;">Top Ranked Consultants</h3>
        <table cellpadding="10" cellspacing="0" border="1" style="border-collapse: collapse; width: 100%;">
          <thead style="background-color: #f5f5f5;">
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Score</th>
              <th>Resume</th>
            </tr>
          </thead>
          <tbody>
            {''.join([
                f"<tr><td>{i+1}</td><td>{c['name']}</td><td>{c['email']}</td><td>{c['score']:.2f}</td><td><a href='{sas_resume_links[c['consultant_id']]}' target='_blank'>View</a></td></tr>"
                for i, c in enumerate(consultants)
            ])}
          </tbody>
        </table>

        <p style="margin-top: 20px;"><em>Note: Resume links are valid for 7 days.</em></p>

        <p>If you need support, contact your admin or team manager.</p>
        <hr />
        <p style="font-size: 12px; color: #888;">This is an automated notification. Please do not reply to this email.</p>
      </body>
    </html>
    """

    message = {
        "senderAddress": sender,
        "content": {
            "subject": f"Your JD {jd_id} has been ranked successfully",
            "plainText": "Greetings, please find the attached consultant ranking report. Resume links are valid for 7 days.",
            "html": html_body
        },
        "recipients": {
            "to": [{"address": to_email}]
        },
        "attachments": [
            {
                "name": f"Consultant_Report_{jd_id}.pdf",
                "contentType": "application/pdf",
                "contentInBase64": encoded_file
            }
        ]
    }

    client = EmailClient.from_connection_string(connection_string)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            poller = client.begin_send(message)
            result = poller.result()

            db.add(EmailNotification(
                jd_id=jd_id,
                recipient_email=to_email,
                status="Sent",
                sent_at=datetime.utcnow()
            ))

            update_workflow_status(db, jd_id, email_status=NotificationStatus.sent)
            return result["status"]

        except Exception as e:
            print(f"❌ Email send attempt {attempt} failed: {str(e)}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)
        else:
            _record_email_failure(db, jd_id, to_email, f"Email send failed after {MAX_RETRIES} attempts")
            raise Exception("Failed to send email after retries.")

def _record_email_failure(db: Session, jd_id: str, email: str, reason: str):
    db.add(EmailNotification(
        jd_id=jd_id,
        recipient_email=email,
        status="Failed",
        sent_at=datetime.utcnow()
    ))

    update_workflow_status(db, jd_id, email_status=NotificationStatus.failed)

def update_workflow_status(db: Session, jd_id: str, email_status: NotificationStatus):
    workflow = db.query(WorkflowStatus).filter_by(jd_id=jd_id).first()
    if workflow:
        workflow.comparison_status = WorkflowStepStatus.completed
        workflow.ranking_status = WorkflowStepStatus.completed
        workflow.email_status = email_status
    db.commit()


# def send_email_with_consultant_report(profile_id: str, recipient_email: str):
#     pdf_buffer = generate_pdf_report_by_consultant(profile_id)
#     pdf_bytes = pdf_buffer.read()

#     email_client = EmailClient.from_connection_string(os.getenv("AZURE_COMM_EMAIL_CONNECTION_STRING"))

#     attachment = {
#         "name": "Consultant_Report.pdf",
#         "attachmentType": "inline",  # or "attachment"
#         "contentType": "application/pdf",  # ✅ important
#         "contentInBase64": base64.b64encode(pdf_bytes).decode()
#     }

#     message = {
#         "senderAddress": os.getenv("EMAIL_SENDER_ADDRESS"),
#         "recipients": {
#             "to": [{"address": recipient_email}]
#         },
#         "content": {
#             "subject": "Consultant Report",
#             "plainText": "Please find the attached consultant ranking report PDF.",
#         },
#         "attachments": [attachment]
#     }

#     try:
#         poller = email_client.begin_send(message)
#         result = poller.result()
#         return {"status": "sent", "message_id": result.message_id}
#     except Exception as e:  
#         return {"status": "failed", "error": str(e)}

# def send_expired_jd_emails():
#     db = SessionLocal()
#     today = date.today()

#     # ✅ Fetch JDs whose end date is today and not completed
#     jds = db.query(JobDescription).filter(
#         JobDescription.end_date == today,
#         JobDescription.status != "completed"
#     ).all()

#     for jd in jds:
#         # ✅ Skip if email already sent
#         existing_email = db.query(EmailNotification).filter_by(jd_id=jd.id, status="Sent").first()
#         if existing_email:
#             continue

#         user = db.query(User).filter(User.id == jd.user_id).first()
#         if not user:
#             continue

#         top_rankings = db.query(Ranking).filter(Ranking.jd_id == jd.id).order_by(Ranking.score.desc()).all()

#         consultants = []
#         for r in top_rankings:
#             profile = db.query(ConsultantProfile).filter_by(id=r.consultant_id).first()
#             if profile:
#                 consultants.append({
#                     "consultant_id": profile.id,
#                     "name": profile.name,
#                     "email": profile.email,
#                     "score": r.score
#                 })

#         # ✅ Proceed only if there are consultants ranked
#         if consultants:
#             pdf_url = generate_sas_url(f"reports/{jd.id}.pdf")
#             try:
#                 send_consultant_report_email(user.email, jd.id, pdf_url, db, consultants)
#                 jd.status = "completed"
#                 db.commit()
#             except Exception as e:
#                 print(f"❌ Failed to send email for JD {jd.id}: {e}")
#                 db.rollback()

#     db.close()

# async def jd_email_scheduler():
#     while True:
#         send_expired_jd_emails()
#         await asyncio.sleep(86400) 



def send_expired_jd_emails():
    db: Session = SessionLocal()
    today = date.today()

    expired_jds = (
        db.query(JobDescription)
        .options(joinedload(JobDescription.rankings), joinedload(JobDescription.user))
        .filter(
            JobDescription.end_date < today,
            JobDescription.status != "completed",
            ~db.query(EmailNotification)
                .filter(
                    EmailNotification.jd_id == JobDescription.id,
                    EmailNotification.status == "Sent"
                )
                .exists()
        )
        .all()
    )

    for jd in expired_jds:
        if jd.rankings:
            sas_url = generate_sas_url(jd.id)
            send_consultant_report_email(jd.id, sas_url)
            db.add(EmailNotification(
                jd_id=jd.id,
                recipient_email=jd.user.email,
                status="Sent"
            ))
    db.commit()



def send_email_with_consultant_report(jd_id: str, recipient_email: str):
    from api.EmailNotification.report_service import generate_consultant_report

    db: Session = SessionLocal()
    try:
        jd = db.query(JobDescription).filter_by(id=jd_id).first()
        if not jd:
            raise Exception("❌ JD not found")

        # 🔎 Get top 3 ranked consultants
        rankings = (
            db.query(Ranking)
            .filter_by(jd_id=jd_id)
            .order_by(Ranking.rank.asc())
            .limit(3)
            .all()
        )

        consultants = []
        for rank in rankings:
            profile = db.query(ConsultantProfile).filter_by(id=rank.profile_id).first()
            if profile:
                consultants.append({
                    "consultant_id": profile.id,
                    "name": profile.name,
                    "email": profile.email,
                    "score": None,  # Optional: fetch from SimilarityScore if needed
                    "explanation": rank.explanation
                })

        # 🧾 Generate full JD report
        pdf_url = generate_consultant_report(jd_id, consultants, jd_obj=jd)

        # 📄 Download PDF and encode
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_bytes = response.content
        encoded_file = base64.b64encode(pdf_bytes).decode("utf-8")

        # 📧 Prepare email
        email_client = EmailClient.from_connection_string(os.getenv("AZURE_COMM_EMAIL_CONNECTION_STRING"))
        attachment = {
            "name": f"Consultant_Report_{jd_id}.pdf",
            "attachmentType": "inline",
            "contentType": "application/pdf",
            "contentInBase64": encoded_file
        }

        message = {
            "senderAddress": os.getenv("EMAIL_SENDER_ADDRESS"),
            "recipients": {
                "to": [{"address": recipient_email}]
            },
            "content": {
                "subject": f"Consultant Report for JD {jd.title}",
                "plainText": "Attached is the consultant ranking report.",
            },
            "attachments": [attachment]
        }

        poller = email_client.begin_send(message)
        result = poller.result()
        return {"status": "sent", "message_id": result.get("messageId")} 

    except Exception as e:
        print(f"❌ Failed to send consultant report email for JD {jd_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
