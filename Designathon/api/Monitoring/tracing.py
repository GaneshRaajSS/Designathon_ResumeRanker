# tracing.py
import os
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.trace import config_integration
from opencensus.ext.requests.trace import trace_integration

# Enable requests integration for HTTP dependency capture
config_integration.trace_integrations(['requests'])
trace_integration()
# Azure Application Insights exporter
exporter = AzureExporter(connection_string=os.getenv("APPINSIGHTS_CONNECTION_STRING"))

# Tracer (sample 100% of requests — adjust if needed)
tracer = Tracer(exporter=exporter, sampler=ProbabilitySampler(1.0))
