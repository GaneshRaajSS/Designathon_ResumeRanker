from fastapi import APIRouter
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
logger = logging.getLogger("monitoring")
logger.setLevel(logging.INFO)
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING")
))
router = APIRouter()

# Azure auth
credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)

log_client = LogsQueryClient(credential)
workspace_id = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")


def query_logs(query: str):
    response = log_client.query_workspace(
        workspace_id=workspace_id,
        query=query,
        timespan=timedelta(hours=2)
    )

    table = response.tables[0]
    columns = table.columns  # ✅ FIXED: list of str
    return [dict(zip(columns, row)) for row in table.rows]


# ✅ 1. Agentic service calls
@router.get("/api/monitoring/agentic-framework")
def view_agentic_framework():
    query = """
    AppDependencies
    | where Target has "openai" or Target has "embedding" or Target has "agent"
    | summarize Count=count() by Target
    | top 10 by Count
    """
    return query_logs(query)

# ✅ 2. Latencies
@router.get("/api/monitoring/latencies")
def get_latencies():
    query = """
    AppDependencies
    | summarize AvgDurationMs = avg(durationMs), Count = count() by Target
    | top 10 by AvgDurationMs desc
    """
    return query_logs(query)


# ✅ 3. Errors
@router.get("/api/monitoring/errors")
def get_error_logs():
    query = """
    AppTraces
    | where SeverityLevel >= 3
    | order by TimeGenerated desc
    | project TimeGenerated, Message, SeverityLevel
    """
    return query_logs(query)

