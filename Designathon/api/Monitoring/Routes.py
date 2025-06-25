from fastapi import APIRouter
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
import threading

# ✅ Configure logger with AzureLogHandler
azure_handler = AzureLogHandler(connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING"))
azure_handler.lock = threading.Lock()

logger = logging.getLogger("monitoring")
logger.setLevel(logging.INFO)
logger.addHandler(azure_handler)

router = APIRouter()

# ✅ Azure Monitor credentials
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
    if not response.tables:
        return []
    table = response.tables[0]
    return [dict(zip(table.columns, row)) for row in table.rows]

# ✅ 1. Agentic service calls
@router.get("/monitoring/agentic-framework")
def view_agentic_framework():
    query = """
    AppDependencies
    | where Target contains "openai" or Target contains "azure" or Name contains "embedding" or Name contains "GPT"
    | summarize Count = count() by Target, Name
    | order by Count desc
    """
    return query_logs(query)

@router.get("/monitoring/latencies")
def get_latencies():
    query = """
    AppDependencies
    | summarize AvgDurationMs = round(avg(todouble(DurationMs)), 2), Count = count() by Target
    | where Count > 3
    | top 10 by AvgDurationMs desc
    """
    try:
        return query_logs(query)
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        logger.exception("❌ Error while querying latencies: %s", e)
        return {"error": str(e), "traceback": traceback_str}


# ✅ 3. View application errors
@router.get("/monitoring/errors")
def get_error_logs():
    query = """
    union AppTraces, AppExceptions
    | where TimeGenerated > ago(24h)
    | where SeverityLevel >= 3
    | order by TimeGenerated desc
    | project TimeGenerated, Message, SeverityLevel
    | take 100
    """
    results = query_logs(query)
    print(f"📊 Query returned {len(results)} rows")
    return results

# ✅ 4. Trigger test error
@router.get("/monitoring/test-error")
def test_error_log():
    try:
        raise ValueError("💥 Test error for Application Insights")
    except Exception:
        logger.exception("Test error occurred!")
    return {"message": "Test error triggered"}
