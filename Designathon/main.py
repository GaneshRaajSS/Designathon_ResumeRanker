# main.py
from fastapi import FastAPI
from api.JobDescription.Routes import router as jd_router
from api.ConsultantProfiles.Routes import router as cp_router
from JDdb import Base, engine

# Create tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Recruitment Matching System")

# Register Job Description routes
app.include_router(jd_router, prefix="/api")
app.include_router(cp_router, prefix="/api")

