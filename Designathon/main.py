from fastapi import FastAPI, Request
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opentelemetry.sdk._logs import LoggingHandler
from JDdb import Base, engine
import logging, time
import os

# Load env variables
load_dotenv()

# Azure Monitor
APPINSIGHTS_CONNECTION_STRING = os.getenv("APPINSIGHTS_CONNECTION_STRING")
configure_azure_monitor(
    connection_string=APPINSIGHTS_CONNECTION_STRING,
    enable_logging=True,
    enable_tracing=True,
    enable_metrics=True,
)

# Set up OpenTelemetry logging
handler = LoggingHandler(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
logger = logging.getLogger("uvicorn.error")
logger.info("Azure Monitor logging initialized.")

# Create DB tables
Base.metadata.create_all(bind=engine)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# FastAPI app
app = FastAPI(title="AI Recruitment Matching System")
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING")
))
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    log_msg = f"{request.method} {request.url.path} completed in {duration:.3f}s with status {response.status_code}"
    logging.info(log_msg)

    return response

app.add_middleware(OpenTelemetryMiddleware)

@app.get("/ping")
async def ping():
    logger.info("Ping endpoint was hit")
    return {"message": "pong"}


@app.on_event("startup")
def on_startup():
    print("🔄 Checking expired Job Descriptions...")
    from api.JobDescription.Service import mark_expired_jds_as_completed
    mark_expired_jds_as_completed()
    print("✅ Expired JDs marked as completed.")


# Include routers
from api.JobDescription.Routes import router as jd_router
from api.ConsultantProfiles.Routes import router as cp_router
from api.Auth.Routes import router as auth_router
from api.SimilarityScore.Routes import router as ss_router
from api.Monitoring.Routes import router as m_router
from api.Ranking.Routes import router as ranking_router
from api.EmailNotification.Routes import router as en_router
from api.WorkflowStatus.Routes import router as wfs_router
from api.JDProfileHistory.Routes import router as jdh_router
from agents.comparison_routes import router as cr_router

app.include_router(jd_router, prefix="/api")
app.include_router(cp_router, prefix="/api")
app.include_router(ss_router, prefix="/api")
app.include_router(m_router, prefix="/api")
app.include_router(auth_router)
app.include_router(ranking_router, prefix="/display")
app.include_router(en_router, prefix="/display")
app.include_router(wfs_router, prefix="/display")
app.include_router(jdh_router, prefix="/display")
app.include_router(cr_router, prefix="/agent")
