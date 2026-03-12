# Usage Guide

This guide covers all features of `azure-functions-logging` with detailed examples.

## Basic Setup

To get started, call `setup_logging()` once and use `get_logger()` to create loggers:

```python
from azure_functions_logging import setup_logging, get_logger

# Initialize logging at the start of your application
setup_logging()

# Get a logger instance for your module
logger = get_logger(__name__)

logger.info("Hello, world!")
```

`setup_logging()` is typically called at module level or in an application startup hook. It only needs to be called once -- subsequent calls are no-ops.

## Colorized Output (Local Development)

By default, `setup_logging()` uses a color-aware formatter designed for local terminal output:

```
14:30:05 INFO my_module Hello, world!
```

Each log level has a distinct color:

| Level | Color | Use Case |
| ----- | ----- | -------- |
| DEBUG | Gray | Detailed diagnostic information |
| INFO | Blue | General operational information |
| WARNING | Yellow | Unexpected events that do not prevent operation |
| ERROR | Red | Errors that caused a specific operation to fail |
| CRITICAL | Bold Red | Fatal errors that prevent the application from continuing |

Colors are automatically disabled when output is redirected to a file or piped to another command.

## JSON Formatting (Production)

For production environments where logs are consumed by aggregation systems (Azure Log Analytics, Datadog, Splunk), switch to JSON formatting:

```python
setup_logging(format="json")
```

Each log line is a single JSON object (NDJSON format):

```json
{"timestamp": "2026-03-12T10:00:00.000000Z", "level": "INFO", "logger": "my_module", "message": "Processing request", "invocation_id": "abc-123", "function_name": "HttpTrigger", "trace_id": "def-456", "cold_start": false}
```

JSON output includes all context fields and any extra fields passed to the logger.

## Context Injection

In Azure Functions handlers, inject the execution context to include function-specific metadata in every log line:

```python
import azure.functions as func
from azure_functions_logging import inject_context, get_logger

logger = get_logger(__name__)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # Inject context at the start of every handler
    inject_context(context)

    logger.info("Handling HTTP request")
    # Output includes: invocation_id, function_name, trace_id, cold_start

    return func.HttpResponse("OK")
```

### What Gets Injected

| Field | Source | Description |
| ----- | ------ | ----------- |
| `invocation_id` | `context.invocation_id` | Unique ID for this function invocation |
| `function_name` | `context.function_name` | Name of the Azure Function |
| `trace_id` | `context.trace_context.trace_id` | Distributed tracing identifier |
| `cold_start` | Automatic | Whether this is the first invocation after process startup |

### Context Scope

Context is stored using Python's `contextvars` module, making it:

- Thread-safe (each thread has its own context)
- Async-safe (each async task has its own context)
- Scoped to the current execution context

You only need to call `inject_context()` once per invocation. All loggers in the same execution context will include the injected fields.

## Context Binding

Bind additional key-value pairs to a logger instance for persistent context across multiple log calls:

```python
logger = get_logger(__name__)

# Create a request-scoped logger with bound context
request_logger = logger.bind(user_id="abc-123", operation="checkout")

request_logger.info("Starting checkout")
# Output includes: user_id=abc-123, operation=checkout

request_logger.info("Validating payment")
# Output includes: user_id=abc-123, operation=checkout

request_logger.info("Checkout complete")
# Output includes: user_id=abc-123, operation=checkout
```

### Immutable Binding

`bind()` returns a **new** logger instance. The original logger is not modified:

```python
logger = get_logger(__name__)
bound = logger.bind(user_id="abc")

bound.info("message")   # includes user_id=abc
logger.info("message")  # does NOT include user_id
```

### Cumulative Binding

Binding is cumulative -- calling `bind()` on an already-bound logger adds to the existing context:

```python
l1 = logger.bind(user_id="abc")
l2 = l1.bind(session_id="xyz")

l2.info("message")
# Output includes both user_id=abc and session_id=xyz
```

### Clearing Context

Remove all bound context from a logger:

```python
bound = logger.bind(user_id="abc")
bound.clear_context()
bound.info("message")
# Output no longer includes user_id
```

## Logger Methods

The `FunctionLogger` returned by `get_logger()` supports all standard logging levels:

```python
logger.debug("Detailed diagnostic information")
logger.info("General operational information")
logger.warning("Something unexpected happened, but process continues")
logger.error("Something went wrong, process might have failed")
logger.critical("Fatal error, process cannot continue")
```

### Exception Logging

Use `logger.exception()` inside an exception handler to include the stack trace:

```python
try:
    result = 1 / 0
except ZeroDivisionError:
    logger.exception("Caught an exception")
    # Output includes the full stack trace automatically
```

### Extra Fields

Pass additional key-value pairs as keyword arguments:

```python
logger.info("User action", action="login", ip="192.168.1.1", duration_ms=42)
```

In JSON format, these appear in the `extra` object. In color format, they appear as `[key=value]` pairs at the end of the line.

## Setting Log Level

Control which messages are output by setting the log level:

```python
import logging

# Show all messages including DEBUG
setup_logging(level=logging.DEBUG)

# Show only WARNING and above
setup_logging(level=logging.WARNING)
```

The default level is `logging.INFO`.

You can also change the level on individual loggers:

```python
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
```

## Cold Start Detection

The library automatically detects cold starts -- the first function invocation after a new Python process is started. This is included as a `cold_start` boolean in log output when `inject_context()` is used.

No manual instrumentation is required. The detection works by tracking whether `inject_context()` has been called before in the current process:

- First call: `cold_start=True`
- All subsequent calls: `cold_start=False`

Restarting the Azure Functions host or the local development server resets the cold start flag.

## host.json Conflict Detection

Azure Functions uses `host.json` to configure logging at the host level. These settings can override your application-level log configuration, silently suppressing log output.

The library reads `host.json` on startup and warns if it detects a conflict:

```
WARNING: host.json logLevel 'Warning' may suppress logs at level 'INFO'
```

### Common Conflicts

| host.json Setting | Application Level | Result |
| ----------------- | ----------------- | ------ |
| `"default": "Warning"` | `logging.INFO` | INFO logs suppressed |
| `"default": "Error"` | `logging.WARNING` | WARNING logs suppressed |
| `"default": "None"` | Any | All logs suppressed |

### Resolution

Adjust `host.json` to match your desired log level:

```json
{
  "logging": {
    "logLevel": {
      "default": "Information"
    }
  }
}
```

Or set a specific override for your function:

```json
{
  "logging": {
    "logLevel": {
      "default": "Warning",
      "Function.MyFunction": "Information"
    }
  }
}
```

## Environment Detection

The library automatically detects whether it is running in Azure or locally:

- **Azure Environment**: Only adds a `ContextFilter` to existing handlers to avoid duplicate log output. The Azure Functions host already configures logging handlers.
- **Local Environment**: Sets up a full handler with the selected formatter for readable developer output.

Detection is based on environment variables:

- `FUNCTIONS_WORKER_RUNTIME` (set to `python` in Azure)
- `WEBSITE_INSTANCE_ID` (set in Azure App Service environments)

## Complete Example

A full Azure Functions HTTP trigger with all logging features:

```python
import logging
import azure.functions as func
from azure_functions_logging import setup_logging, get_logger, inject_context

# Module-level setup (runs once on cold start)
setup_logging(format="json", level=logging.INFO)
logger = get_logger(__name__)

app = func.FunctionApp()

@app.route(route="process")
def process_request(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # Inject Azure Functions context
    inject_context(context)

    # Create a request-scoped logger
    request_logger = logger.bind(
        method=req.method,
        url=req.url,
    )

    request_logger.info("Request received")

    try:
        body = req.get_json()
        user_id = body.get("user_id")

        # Further scope the logger
        user_logger = request_logger.bind(user_id=user_id)
        user_logger.info("Processing user request")

        # Business logic here...
        result = {"status": "ok"}

        user_logger.info("Request completed", status="success")
        return func.HttpResponse(json.dumps(result), mimetype="application/json")

    except Exception:
        request_logger.exception("Request failed")
        return func.HttpResponse("Internal error", status_code=500)
```

Each log line includes: timestamp, level, logger name, message, invocation_id, function_name, trace_id, cold_start, method, url, user_id (when bound), and any extra fields.
