# from apscheduler.schedulers.background import BackgroundScheduler
# from db.Model import Application, JobDescription, ConsultantProfile
# from JDdb import SessionLocal
# from agents.ranking_service import rank_profiles, finalize_and_notify
# import asyncio

# app_scheduler = BackgroundScheduler()

# @app_scheduler.scheduled_job("interval", days=3)
# def rerank_every_3_days():
#     db = SessionLocal()
#     try:
#         all_apps = db.query(Application).all()
#         for app in all_apps:
#             jd = db.query(JobDescription).filter(JobDescription.id == app.jd_id).first()
#             profile = db.query(ConsultantProfile).filter(ConsultantProfile.id == app.consultant_id).first()
#             if jd and profile:
#                 asyncio.run(rank_profiles(jd, [profile]))
#                 asyncio.run(finalize_and_notify(jd.id, [profile]))
#     finally:
#         db.close()

# app_scheduler.start()