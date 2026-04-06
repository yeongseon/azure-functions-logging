# Deployment Guide

This guide walks through deploying the `examples/e2e_app` sample to Azure Functions and verifying structured JSON logging end-to-end. It includes required code changes for Azure-hosted logging behavior, resource provisioning, publish, endpoint checks, and log queries in Application Insights. Outputs are representative examples, not guaranteed byte-for-byte.

## Prerequisites

| Requirement | Minimum | Notes |
|---|---|---|
| Azure subscription | Active | Use `<YOUR_SUBSCRIPTION_ID>` |
| Azure CLI (`az`) | Current | `az --version` |
| Azure Functions Core Tools (`func`) | v4 | `func --version` |
| Python | 3.10+ | Deploy runtime shown is Python 3.11 |
| Storage Account | StorageV2 | Required by Azure Functions runtime |
| Application Insights | Workspace-based component | Required for log queries |
| Package version | `azure-functions-logging==0.4.1` | Guide aligned to v0.4.1 behavior |

From `examples/e2e_app`, install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Representative output:

```bash
Requirement already satisfied: pip in ./.venv/lib/python3.11/site-packages (25.0)
Collecting azure-functions
Collecting azure-functions-logging==0.4.1
Successfully installed azure-functions-1.21.0 azure-functions-logging-0.4.1
```

## Code changes for Azure deployment

The shipped `e2e_app` calls `afl.setup_logging()` with defaults. In Azure (`FUNCTIONS_WORKER_RUNTIME` is set), `setup_logging()` does not add handlers and does not set levels; it only adds `ContextFilter` to root handlers.

To guarantee structured NDJSON in Azure, pass `functions_formatter=afl.JsonFormatter()`:

```python
import azure_functions_logging as afl

# Use JsonFormatter for structured NDJSON output in Azure
afl.setup_logging(functions_formatter=afl.JsonFormatter())
```

For cleaner deployment code, use `@afl.with_context` instead of manual `inject_context(...)` calls; this still feeds `invocation_id`, `function_name`, `trace_id`, and `cold_start` into `ContextFilter` on each invocation.

### Modified `function_app.py`

```python
"""E2E test function app for azure-functions-logging."""
from __future__ import annotations

import json
import logging

import azure.functions as func

import azure_functions_logging as afl

# Use JsonFormatter for structured NDJSON output in Azure
afl.setup_logging(functions_formatter=afl.JsonFormatter())

app = func.FunctionApp()


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"status": "ok"}), mimetype="application/json")


@app.route(route="logme", auth_level=func.AuthLevel.ANONYMOUS)
@afl.with_context
def logme(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logger = afl.get_logger(__name__)
    correlation_id = req.params.get("correlation_id", "e2e-test")
    logger.info("e2e log entry", extra={"correlation_id": correlation_id})
    logging.info("e2e stdlib log: correlation_id=%s", correlation_id)
    return func.HttpResponse(
        json.dumps({"logged": True, "correlation_id": correlation_id}),
        mimetype="application/json",
    )
```

### `host.json` used by `e2e_app`

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": false
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

## Provision Azure resources

```bash
az account set --subscription <YOUR_SUBSCRIPTION_ID>
az group create --name <YOUR_RESOURCE_GROUP> --location eastus
```

Representative output:

```json
{"name":"<YOUR_RESOURCE_GROUP>","location":"eastus","properties":{"provisioningState":"Succeeded"}}
```

```bash
az storage account create --name <YOUR_STORAGE_ACCOUNT> --resource-group <YOUR_RESOURCE_GROUP> --location eastus --sku Standard_LRS --kind StorageV2
```

Representative output:

```json
{"name":"<YOUR_STORAGE_ACCOUNT>","kind":"StorageV2","provisioningState":"Succeeded"}
```

```bash
az monitor log-analytics workspace create --resource-group <YOUR_RESOURCE_GROUP> --workspace-name <YOUR_LOG_ANALYTICS_WORKSPACE> --location eastus
```

Representative output:

```json
{"name":"<YOUR_LOG_ANALYTICS_WORKSPACE>","location":"eastus","provisioningState":"Succeeded"}
```

```bash
WORKSPACE_ID=$(az monitor log-analytics workspace show --resource-group <YOUR_RESOURCE_GROUP> --workspace-name <YOUR_LOG_ANALYTICS_WORKSPACE> --query id --output tsv)
az monitor app-insights component create --app <YOUR_APP_INSIGHTS_NAME> --resource-group <YOUR_RESOURCE_GROUP> --location eastus --kind web --application-type web --workspace "$WORKSPACE_ID"
```

Representative output:

```json
{"appId":"<YOUR_APP_INSIGHTS_APP_ID>","name":"<YOUR_APP_INSIGHTS_NAME>","location":"eastus","provisioningState":"Succeeded"}
```

```bash
az functionapp create --name <YOUR_FUNCTION_APP_NAME> --resource-group <YOUR_RESOURCE_GROUP> --storage-account <YOUR_STORAGE_ACCOUNT> --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4 --app-insights <YOUR_APP_INSIGHTS_NAME>
```

Representative output:

```json
{"name":"<YOUR_FUNCTION_APP_NAME>","defaultHostName":"<YOUR_FUNCTION_APP_NAME>.azurewebsites.net","provisioningState":"Succeeded","state":"Running"}
```

## Configure app settings

```bash
az functionapp config appsettings set --name <YOUR_FUNCTION_APP_NAME> --resource-group <YOUR_RESOURCE_GROUP> --settings FUNCTIONS_WORKER_RUNTIME=python
```

Representative output:

```json
[{"name":"FUNCTIONS_WORKER_RUNTIME","slotSetting":false,"value":""}]
```

## Publish

From `examples/e2e_app`:

```bash
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```

Representative output:

```text
Getting site publishing info...
[2025-01-15T10:27:41.021Z] Starting the function app deployment...
Uploading package...
Uploading 2.31 MB [#############################################################################]
Deployment completed successfully.
Syncing triggers...
Functions in <YOUR_FUNCTION_APP_NAME>:
    health - [httpTrigger]
        Invoke url: https://<YOUR_FUNCTION_APP_NAME>.azurewebsites.net/api/health
    logme - [httpTrigger]
        Invoke url: https://<YOUR_FUNCTION_APP_NAME>.azurewebsites.net/api/logme
Deployment successful.
```

## Verify endpoints

```bash
export BASE_URL="https://<YOUR_FUNCTION_APP_NAME>.azurewebsites.net"
```

### `GET /api/health`

```bash
curl -i -s "$BASE_URL/api/health"
```

Representative response:

```text
HTTP/1.1 200 OK
Content-Type: application/json

{"status":"ok"}
```

### `GET /api/logme?correlation_id=demo-123`

```bash
curl -i -s "$BASE_URL/api/logme?correlation_id=demo-123"
```

Representative response:

```text
HTTP/1.1 200 OK
Content-Type: application/json

{"logged":true,"correlation_id":"demo-123"}
```

## Verify structured logs via `func logstream`

```bash
func azure functionapp logstream <YOUR_FUNCTION_APP_NAME>
```

Representative output:

```text
Connecting to log-streaming service...
2025-01-15T10:35:00Z   [Information]   Executing 'Functions.logme' (Reason='This function was programmatically called via the host APIs.', Id=ab2a5eb3-1f80-46ea-a818-601ca6ed1111)
{"timestamp":"2025-01-15T10:35:00.123456+00:00","level":"INFO","logger":"function_app","message":"e2e log entry","invocation_id":"ab2a5eb3-1f80-46ea-a818-601ca6ed1111","function_name":"logme","trace_id":null,"cold_start":null,"exception":null,"extra":{"correlation_id":"demo-123"}}
2025-01-15T10:35:00Z   [Information]   Executed 'Functions.logme' (Succeeded, Id=ab2a5eb3-1f80-46ea-a818-601ca6ed1111, Duration=19ms)
```

That NDJSON line is emitted by `afl.get_logger(__name__)`. Without `functions_formatter=afl.JsonFormatter()`, Azure host handlers keep their own format and output is host-dependent.

## Application Insights query examples

Get the Application Insights App ID:

```bash
APP_INSIGHTS_APP_ID=$(az monitor app-insights component show --app <YOUR_APP_INSIGHTS_NAME> --resource-group <YOUR_RESOURCE_GROUP> --query appId --output tsv)
```

Representative output:

```text
<YOUR_APP_INSIGHTS_APP_ID>
```

Query by `correlation_id` from the structured JSON payload:

```bash
az monitor app-insights query --app "$APP_INSIGHTS_APP_ID" --analytics-query "traces | where timestamp > ago(30m) | extend payload=parse_json(message) | where tostring(payload.extra.correlation_id) == 'demo-123' | project timestamp, severityLevel, logger=tostring(payload.logger), function_name=tostring(payload.function_name), invocation_id=tostring(payload.invocation_id), message=tostring(payload.message) | order by timestamp desc"
```

Representative output:

```json
{"tables":[{"name":"PrimaryResult","columns":[{"name":"timestamp","type":"datetime"},{"name":"severityLevel","type":"int"},{"name":"logger","type":"string"},{"name":"function_name","type":"string"},{"name":"invocation_id","type":"string"},{"name":"message","type":"string"}],"rows":[["2025-01-15T10:35:00.123Z",1,"function_app","logme","ab2a5eb3-1f80-46ea-a818-601ca6ed1111","e2e log entry"]]}]}
```

Equivalent KQL for the Azure portal Logs UI:

```kusto
traces
| where timestamp > ago(30m)
| extend payload = parse_json(message)
| where tostring(payload.extra.correlation_id) == "demo-123"
| project timestamp, severityLevel, logger=tostring(payload.logger), function_name=tostring(payload.function_name), invocation_id=tostring(payload.invocation_id), message=tostring(payload.message)
| order by timestamp desc
```

## Cleanup

```bash
az group delete --name <YOUR_RESOURCE_GROUP> --yes --no-wait
```

Representative output:

```text
{"status":"Accepted"}
```

## Sources

- [Azure Functions Python quickstart](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python)
- [Azure Functions Core Tools publish reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-core-tools-reference#func-azure-functionapp-publish)
- [Application Insights for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Function App settings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings)
- [Functions monitoring and telemetry](https://learn.microsoft.com/en-us/azure/azure-functions/analyze-telemetry-data)

## See Also

- [`azure-functions-doctor`](https://github.com/yeongseon/azure-functions-doctor)
- [`azure-functions-scaffold`](https://github.com/yeongseon/azure-functions-scaffold)
