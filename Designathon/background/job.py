from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from azure.storage.blob import BlobServiceClient, StandardBlobTier
from db.Model import Application, JobDescription, ConsultantProfile
from JDdb import SessionLocal
from agents.ranking_service import rank_profiles, finalize_and_notify
import asyncio
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
import threading
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", message="Timezone offset does not match system offset")

load_dotenv()


# ✅ Logger setup for Azure Monitor
azure_handler = AzureLogHandler(connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING"))
azure_handler.lock = threading.Lock()

logger = logging.getLogger("resume_scheduler")
logger.setLevel(logging.INFO)
logger.addHandler(azure_handler)

# ✅ Azure Blob Setup
blob_service_client = BlobServiceClient.from_connection_string(
    f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};"
    f"AccountKey={os.getenv('AZURE_STORAGE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"
)
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# ✅ Create ONE unified APScheduler
app_scheduler = BackgroundScheduler()

# 🔁 Rerank every 3 days
@app_scheduler.scheduled_job("interval", days=3)
def rerank_every_3_days():
    logger.info("🔁 Starting rerank_every_3_days job...")
    db = SessionLocal()
    try:
        all_apps = db.query(Application).all()
        for app in all_apps:
            jd = db.query(JobDescription).filter(JobDescription.id == app.jd_id).first()
            profile = db.query(ConsultantProfile).filter(ConsultantProfile.id == app.consultant_id).first()
            if jd and profile:
                asyncio.run(rank_profiles(jd, [profile]))
                asyncio.run(finalize_and_notify(jd.id, [profile]))
        logger.info("✅ Finished rerank job.")
    except Exception as e:
        logger.exception(f"❌ Error in rerank job: {e}")
    finally:
        db.close()

# 🧊 Move resumes to Cool tier after 21 days
@app_scheduler.scheduled_job("interval", days=1)
def move_old_resumes_to_cool_tier():
    logger.info("🧊 Checking resumes for Cool tier transition...")
    container_client = blob_service_client.get_container_client(container_name)
    now = datetime.now(timezone.utc)

    for blob in container_client.list_blobs(name_starts_with="resumes/"):
        if blob.last_modified < (now - timedelta(days=21)):
            blob_client = container_client.get_blob_client(blob.name)
            try:
                blob_client.set_standard_blob_tier(StandardBlobTier.Cool)
                logger.info(f"Moved blob '{blob.name}' to Cool tier (Last Modified: {blob.last_modified})")
            except Exception as e:
                logger.exception(f"Error moving blob '{blob.name}' to Cool tier: {str(e)}")

    logger.info("✅ Resume tier check completed.")

# ✅ Start all jobs
app_scheduler.start()
