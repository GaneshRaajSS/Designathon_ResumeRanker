from db.Model import SimilarityScore, JobDescription, User, Ranking, WorkflowStatus, JDProfileHistory
from api.EmailNotification.report_service import generate_consultant_report
from api.EmailNotification.Service import send_consultant_report_email
from .similarity_service import compute_cosine_similarity
from .embedding_service import gpt_score_resume
from api.JDHistory.Service import create_history_entry
from api.ConsultantProfiles.Service import move_resume_to_jd_folder
from JDdb import SessionLocal
from enums import WorkflowStepStatus, NotificationStatus, HistoryStatus
from sqlalchemy.orm import Session
from sqlalchemy import delete

async def rank_profiles(jd, profiles):
    scores = compute_cosine_similarity(jd.embedding, [p.embedding for p in profiles])
    db = SessionLocal()
    try:
        for profile, score in zip(profiles, scores):
            db.add(SimilarityScore(jd_id=jd.id, profile_id=profile.id, similarity_score=score))
        db.commit()
        top_10 = sorted(zip(profiles, scores), key=lambda x: x[1], reverse=True)[:10]

        reranked = []
        for profile, sim_score in top_10:
            explanation = await gpt_score_resume(jd, profile)
            reranked.append((profile, sim_score, explanation))

        # Sort by score again to assign proper rank
        reranked = sorted(reranked, key=lambda x: x[1], reverse=True)

        # Clear existing rankings for this JD
        db.query(Ranking).filter_by(jd_id=jd.id).delete()
        db.query(JDProfileHistory).filter_by(jd_id=jd.id).delete()
        db.commit()

        top_ranked_profiles = []
        for rank, (profile, score, explanation) in enumerate(reranked, start=1):
            db.add(Ranking(jd_id=jd.id, profile_id=profile.id, rank=rank, explanation=explanation))

            if rank == 1:
                action_status = HistoryStatus.Shortlisted
                await move_resume_to_jd_folder(profile.id, jd.id)
            else:
                action_status = HistoryStatus.Rejected

            create_history_entry({
                "jd_id": jd.id,
                "profile_id": profile.id,
                "action": action_status,
            })
            top_ranked_profiles.append(profile)

        db.commit()

        return [
            {
                "consultant_id": profile.id,
                "name": profile.name,
                "email": profile.email,
                "score": score,
                "explanation": explanation
            }
            for profile, score, explanation in reranked[:1]  # Currently top 1 only
        ]

    finally:
        db.close()

async def finalize_and_notify(jd_id: str, ranked_consultants: list[dict]):
    db = SessionLocal()
    try:
        jd = db.query(JobDescription).filter_by(id=jd_id).first()
        if not jd:
            print("❌ JD not found.")
            return

        ar_user = db.query(User).filter_by(user_id=jd.user_id).first()
        if not ar_user:
            print("❌ No ARRequestor found for JD.")
            return

        # Generate PDF with full JD + consultants
        pdf_url = generate_consultant_report(jd_id, ranked_consultants, jd_obj=jd)

        # Send email with consultant details
        print(f"📨 Sending email to: {ar_user.email}")
        status = send_consultant_report_email(ar_user.email, jd_id, pdf_url, db, ranked_consultants)
        print(f"📧 Email sent status: {status}")

    except Exception as e:
        print(f"❌ Error during finalize_and_notify: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def init_or_update_workflow_status(db: Session, jd_id: str):
    existing = db.query(WorkflowStatus).filter_by(jd_id=jd_id).first()

    if existing:
        existing.comparison_status = WorkflowStepStatus.completed.value
        existing.ranking_status = WorkflowStepStatus.completed.value
        existing.email_status = NotificationStatus.pending.value
    else:
        new_status = WorkflowStatus(
            jd_id=jd_id,
            comparison_status=WorkflowStepStatus.completed.value,
            ranking_status=WorkflowStepStatus.pending.value,
            email_status=NotificationStatus.pending.value,
        )
        db.add(new_status)

    db.commit()