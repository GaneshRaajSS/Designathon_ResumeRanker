from db.Model import SimilarityScore
from db.Model import Ranking
from .similarity_service import compute_cosine_similarity
from .embedding_service import gpt_score_resume
from api.JDHistory.Service import create_history_entry
from api.ConsultantProfiles.Service import move_resume_to_jd_folder
from JDdb import SessionLocal

async def rank_profiles(jd, profiles):
    scores = compute_cosine_similarity(jd.embedding, [p.embedding for p in profiles])
    db = SessionLocal()
    try:
        for profile, score in zip(profiles, scores):
            db.add(SimilarityScore(jd_id=jd.id, profile_id=profile.id, similarity_score=score))
        db.commit()

        top_10 = sorted(zip(profiles, scores), key=lambda x: x[1], reverse=True)[:2]

        reranked = []
        for profile, sim_score in top_10:
            explanation = await gpt_score_resume(jd, profile)
            reranked.append((profile, sim_score, explanation))

        reranked = sorted(reranked, key=lambda x: x[1], reverse=True)[:1]
        top_ranked_profiles = []
        for rank, (profile, score, explanation) in enumerate(reranked, start=1):
            db.add(Ranking(jd_id=jd.id, profile_id=profile.id, rank=rank,  explanation=explanation))
            create_history_entry({
                "jd_id": jd.id,
                "profile_id": profile.id,
                "action": "gpt-ranked",
            })
            top_ranked_profiles.append(profile)
        db.commit()

        for ranked in top_ranked_profiles:
            await move_resume_to_jd_folder(ranked.id, jd.id)
    finally:
        db.close()
