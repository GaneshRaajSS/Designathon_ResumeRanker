from fastapi import APIRouter, BackgroundTasks
from JDdb import SessionLocal
from db.Model import JobDescription
from db.Model import ConsultantProfile
from db.Model import Ranking
from agents.ranking_service import rank_profiles

router = APIRouter()

active_jobs = set()

@router.post("/compare-and-rank/{jd_id}")
def compare_and_rank(jd_id: str, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        # Early exit if already ranked
        if db.query(Ranking).filter(Ranking.jd_id == jd_id).first():
            return {"message": f"JD {jd_id} has already been ranked."}
    finally:
        db.close()

    if jd_id in active_jobs:
        return {"message": "Already processing this JD"}

    active_jobs.add(jd_id)
    background_tasks.add_task(run_ranking_task, jd_id)
    return {"message": "Ranking queued"}


async def run_ranking_task(jd_id):
    db = SessionLocal()
    try:
        # Check if JD already has rankings
        existing_ranking = db.query(Ranking).filter(Ranking.jd_id == jd_id).first()
        if existing_ranking:
            print(f"JD {jd_id} already ranked. Skipping...")
            return

        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            print(f"JD {jd_id} not found.")
            return

        profiles = db.query(ConsultantProfile).all()
        await rank_profiles(jd, profiles)

    finally:
        active_jobs.discard(jd_id)
        db.close()

