# main.py
from api.JobDescription.Routes import router as jd_router
from api.JobDescription.Service import mark_expired_jds_as_completed
from api.ConsultantProfiles.Routes import router as cp_router
from api.Auth.Routes import router as auth_router
from agents.comparison_routes import router as cr_router
from JDdb import Base, engine
from fastapi import FastAPI
from dotenv import load_dotenv
from urllib.parse import urlencode

# Create tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Recruitment Matching System")

@app.on_event("startup")
def on_startup():
    print("🔄 Checking expired Job Descriptions...")
    mark_expired_jds_as_completed()
    print("✅ Expired JDs marked as completed.")

# Register Job Description routes
app.include_router(jd_router, prefix="/api")
app.include_router(cp_router, prefix="/api")
app.include_router(auth_router)

app.include_router(cr_router, prefix="/agent")

