from fastapi import FastAPI, Request
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from JDdb import Base, engine
import logging
import time
import os
import threading
from opencensus.ext.azure.log_exporter import AzureLogHandler
# from api.ConsultantProfiles.blob_tier import scheduler
# from api.Application.AppBackground import app_scheduler

# ✅ Load environment variables
load_dotenv()

# ✅ Configure Azure Monitor
configure_azure_monitor(
    connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING"),
    enable_logging=True,
    enable_tracing=True,
    enable_metrics=True,
)

# ✅ Setup AzureLogHandler with threading lock (for Python 3.12+)
azure_handler = AzureLogHandler(connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING"))
azure_handler.lock = threading.Lock()

# ✅ Setup main logger
logger = logging.getLogger("monitoring")
logger.setLevel(logging.INFO)
logger.addHandler(azure_handler)

# ✅ Optional: Add to Uvicorn logger too
uvicorn_logger = logging.getLogger("uvicorn.error")
uvicorn_logger.setLevel(logging.INFO)
uvicorn_logger.addHandler(azure_handler)

# ✅ Create DB tables
Base.metadata.create_all(bind=engine)

# ✅ Initialize FastAPI app
app = FastAPI(title="AI Recruitment Matching System")
app.add_middleware(OpenTelemetryMiddleware)

# ✅ Middleware for request timing logs
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} completed in {duration:.2f}s with status {response.status_code}")
    return response

@app.get("/ping")
async def ping():
    logger.info("Ping endpoint hit")
    return {"message": "pong"}

@app.on_event("startup")
def on_startup():
    print("🔄 Checking expired Job Descriptions...")
    from api.JobDescription.Service import mark_expired_jds_as_completed
    mark_expired_jds_as_completed()
    print("✅ Expired JDs marked as completed.")
    from background.job import app_scheduler
    if not app_scheduler.running:
        app_scheduler.start()
    print("✅ Schedulers are being called.")



# ✅ Include routers
from api.JobDescription.Routes import router as jd_router
from api.ConsultantProfiles.Routes import router as cp_router
from api.Auth.Routes import router as auth_router
from api.SimilarityScore.Routes import router as ss_router
from api.Monitoring.Routes import router as m_router
from api.Ranking.Routes import router as ranking_router
from api.Application.Routes import router as app_router
from api.EmailNotification.Routes import router as en_router
from api.WorkflowStatus.Routes import router as wfs_router
from api.JDProfileHistory.Routes import router as jdh_router
# from agents.comparison_routes import router as cr_router


app.include_router(jd_router, prefix="/api")
app.include_router(cp_router, prefix="/api")
app.include_router(ss_router, prefix="/api")
app.include_router(app_router, prefix="/api")
app.include_router(m_router, prefix="/api")
app.include_router(auth_router)
app.include_router(ranking_router, prefix="/display")
app.include_router(en_router, prefix="/display")
app.include_router(wfs_router, prefix="/display")
app.include_router(jdh_router, prefix="/display")
# app.include_router(cr_router, prefix="/agent")
