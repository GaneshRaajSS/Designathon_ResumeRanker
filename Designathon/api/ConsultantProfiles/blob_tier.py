from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient, StandardBlobTier
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
import threading

# ✅ Azure Blob Setup
blob_service_client = BlobServiceClient.from_connection_string(
    f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};"
    f"AccountKey={os.getenv('AZURE_STORAGE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"
)
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# ✅ Logger with Azure Monitor
azure_handler = AzureLogHandler(connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING"))
azure_handler.lock = threading.Lock()

logger = logging.getLogger("blob_tier_logger")
logger.setLevel(logging.INFO)
logger.addHandler(azure_handler)
