# Usage Guide

Quickly set up and use Azure Functions Logging in your project.

## Basic Setup

To get started, you only need to call `setup_logging()` once and then use `get_logger()` to create loggers.

```python
from azure_functions_logging import setup_logging, get_logger

# Initialize logging at the start of your application
setup_logging()

# Get a logger instance for your module
logger = get_logger(__name__)

logger.info("Hello, world!")
```

## Colorized Output (Local Development)

By default, `setup_logging()` uses a color-aware formatter designed for local terminal output. The format is:

`HH:MM:SS LEVEL logger message [context_fields]`

- **DEBUG**: Gray
- **INFO**: Blue
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Bold Red

## JSON Formatting (Production)

For production environments, you can switch to JSON formatting which is more suitable for log aggregation systems.

```python
setup_logging(format="json")
```

The output will be NDJSON (Newline Delimited JSON), with each log line being a single JSON object:

```json
{"timestamp": "2024-03-12T10:00:00Z", "level": "INFO", "logger": "root", "message": "Starting process", "invocation_id": "...", "function_name": "...", "trace_id": "...", "cold_start": false}
```

## Context Injection

In an Azure Functions handler, you should inject the `context` object to automatically include function-specific fields in your logs.

```python
import azure.functions as func
from azure_functions_logging import inject_context, get_logger

logger = get_logger(__name__)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # This automatically sets invocation_id, function_name, trace_id, and cold_start status
    inject_context(context)
    
    logger.info("Handling HTTP request")
    return func.HttpResponse("OK")
```

## Context Binding

You can bind extra key-value pairs to a logger instance. This is useful for passing around context without having to include it in every log call manually.

```python
# Returns a new FunctionLogger instance with the bound context
user_logger = logger.bind(user_id="abc-123", session_id="xyz")

user_logger.info("Processing user request") 
# Output will include user_id and session_id
```

## Logger Methods

The `FunctionLogger` returned by `get_logger()` supports all standard logging levels:

```python
logger.debug("Detailed diagnostic information")
logger.info("General operational information")
logger.warning("Something unexpected happened, but process continues")
logger.error("Something went wrong, process might have failed")
logger.critical("Fatal error, process cannot continue")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Caught an exception") # Includes stack trace automatically
```

## Cold Start Detection

The library automatically detects if the current invocation is part of a cold start. This status is included as a `cold_start` boolean in your logs when `inject_context()` is used. No manual instrumentation is required beyond calling `inject_context()`.

## host.json Conflicts

!!! warning
    If you have configured `logging` in your `host.json`, those settings might conflict with `setup_logging()`. The library will detect these situations and log a warning to help you resolve the conflict.

## Environment Detection

The library includes logic to detect if it's running in a real Azure Functions environment or a local environment:

- **Azure Environment**: The library only adds a filter to existing handlers to avoid duplicating logs or interfering with Azure's internal logging setup.
- **Local Environment**: The library sets up a full handler and formatter to provide readable output for developers.
