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
from api.ConsultantProfiles.Extractor import extract_sections 
def parse_years(yoe_str: str) -> float:
    import re
    match = re.match(r"(\d+(\.\d+)?)", yoe_str)
    return float(match.group(1)) if match else 0.0

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

async def rank_profiles(jd, profiles):
    db = SessionLocal()
    try:
        # Fetch all saved similarity scores for this JD
        existing_scores = {
            s.profile_id: s.similarity_score
            for s in db.query(SimilarityScore).filter_by(jd_id=jd.id).all()
        }

        #  Filter profiles with saved similarity scores
        profiles_with_scores = []
        for p in profiles:
            if p.id in existing_scores:
                profiles_with_scores.append((p, existing_scores[p.id]))
            else:
                print(f"⚠️ Skipping profile {p.name} — no saved similarity score.")

        if not profiles_with_scores:
            print("⚠️ No profiles with valid similarity scores.")
            return []

        # Pick top 5 by similarity
        top_5 = sorted(profiles_with_scores, key=lambda x: x[1], reverse=True)[:5]

        #  Re-rank top 5 with GPT
        reranked = []
        for profile, sim_score in top_5:
            gpt_result = await gpt_score_resume(jd, profile)

            # Handle different return types from gpt_score_resume
            if isinstance(gpt_result, tuple):
                gpt_score, explanation = gpt_result
            elif isinstance(gpt_result, dict):
                gpt_score = gpt_result.get("score", sim_score)
                explanation = gpt_result.get("explanation", "")
            else:
                gpt_score = sim_score
                explanation = str(gpt_result)

            reranked.append((profile, sim_score, gpt_score, explanation))

        #  Sort by GPT score
        reranked = sorted(reranked, key=lambda x: x[2], reverse=True)

        # Compare new top 3 with existing
        existing_top3 = (
            db.query(Ranking.profile_id)
            .filter_by(jd_id=jd.id)
            .order_by(Ranking.rank)
            .limit(3)
            .all()
        )
        existing_ids = [r[0] for r in existing_top3]
        new_ids = [p.id for p, _, _, _ in reranked[:3]]

        top3_changed = set(existing_ids) != set(new_ids)

        # Clear previous rankings and history
        db.query(Ranking).filter_by(jd_id=jd.id).delete()
        db.query(JDProfileHistory).filter_by(jd_id=jd.id).delete()
        db.commit()

        ranked_consultants = []
        for rank, (profile, sim_score, gpt_score, explanation) in enumerate(reranked[:3], start=1):
            db.add(Ranking(
                jd_id=jd.id,
                profile_id=profile.id,
                rank=rank,
                explanation=explanation,
            ))
            print(f"🔁 Saved Rank {rank}: {profile.name} ({profile.id})")

            # Top 3 are all shortlisted
            action_status = HistoryStatus.Shortlisted
            await move_resume_to_jd_folder(profile.id, jd.id)

            create_history_entry({
                "jd_id": jd.id,
                "profile_id": profile.id,
                "action": action_status,
            }, db)

            ranked_consultants.append({
                "consultant_id": profile.id,
                "name": profile.name,
                "email": profile.email,
                "score": gpt_score,
                "explanation": explanation
            })

        db.commit()

        if top3_changed:
            print("📧 Top 3 changed — sending report")
            await finalize_and_notify(jd.id, ranked_consultants)
        else:
            print("✅ Top 3 unchanged — no email sent")

        return ranked_consultants

    except Exception as e:
        db.rollback()
        print(f"❌ Error in rank_profiles: {e}")
        raise
    finally:
        db.close()
