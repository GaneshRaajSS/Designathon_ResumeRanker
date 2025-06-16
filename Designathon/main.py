# main.py
from fastapi import FastAPI
from api.JobDescription.Routes import router as jd_router
from api.JobDescription.Service import mark_expired_jds_as_completed
from api.ConsultantProfiles.Routes import router as cp_router
from agents.comparison_routes import router as cr_router
from JDdb import Base, engine

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
app.include_router(cr_router, prefix="/agent")

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from api.JobDescription.Routes import router as jd_router
# from api.ConsultantProfiles.Routes import router as cp_router
# from agents.comparison_routes import router as cr_router
# from api.UserProfiles.Routes import router as user_router  # Add this
# from JDdb import Base, engine
# import os
# from dotenv import load_dotenv

# load_dotenv()

# OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
# OKTA_ISSUER = os.getenv("OKTA_ISSUER")

# if not OKTA_CLIENT_ID:
#     raise ValueError("OKTA_CLIENT_ID is not set in the environment!")

# if not OKTA_ISSUER:
#     raise ValueError("OKTA_ISSUER is not set in the environment!")

# # FastAPI App with OAuth2 Swagger UI
# app = FastAPI(
#     title="Resume Ranker",
#     description="Secure Resume-JD Matching with Okta Auth",
#     swagger_ui_init_oauth={
#         "clientId": OKTA_CLIENT_ID,
#         "usePkceWithAuthorizationCodeGrant": True,
#         "scopes": "openid email profile"
#     }
# )

# # CORS for local testing (adjust in prod)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # change this to specific domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Create DB tables
# Base.metadata.create_all(bind=engine)

# # Include routers
# app.include_router(jd_router, prefix="/api")
# app.include_router(cp_router, prefix="/api")
# app.include_router(cr_router, prefix="/agent")
# app.include_router(user_router, prefix="/api")  # Add user routes

# @app.get("/")
# async def root():
#     return {"message": "Resume Ranker API with Okta Authentication"}