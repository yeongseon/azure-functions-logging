# Azure Functions Logging

Developer-friendly logging helpers for the Azure Functions Python v2 programming model.

Azure Functions Logging provides a thin wrapper around Python's standard `logging` module to make logging in Azure Functions more developer-friendly. It handles context injection, cold start detection, and provides clean, colorized output for local development and structured JSON formatting for production environments.

## The Problem

Azure Functions Python handlers share common logging pain points:

- Log output is visually dense and hard to scan during local development
- Errors do not stand out from info-level noise
- Default formatting is not optimized for human readability
- There is no built-in way to include invocation context (invocation ID, function name, trace ID) in log output
- Cold start detection requires manual instrumentation
- Switching between human-readable and machine-parseable formats requires boilerplate

## The Solution

`azure-functions-logging` provides a one-liner setup that handles all of these concerns:

```python
from azure_functions_logging import setup_logging, get_logger, inject_context

setup_logging()
logger = get_logger(__name__)
```

That is all the configuration needed. The library detects whether it is running locally or in Azure and adjusts its behavior accordingly.

## Key Features

- **Colorized Output** -- Clean, readable logs with color-coded levels during local development (DEBUG gray, INFO blue, WARNING yellow, ERROR red, CRITICAL bold red)
- **JSON Formatting** -- NDJSON structured output for production environments, compatible with Azure Log Analytics and other log aggregation systems
- **Context Injection** -- Automatically include invocation IDs, function names, and trace IDs in every log line via `inject_context(context)`
- **Cold Start Detection** -- Automatically detect and flag cold starts in your logs without manual instrumentation
- **Context Binding** -- Bind additional key-value pairs to loggers for persistent context across multiple log calls via `logger.bind(user_id="abc")`
- **Host Config Warning** -- Automatically detect and warn about potential `host.json` logging level conflicts that silently suppress log output
- **Idempotent Setup** -- Calling `setup_logging()` multiple times is safe and will not cause double-logging
- **Zero Dependencies** -- Uses only the Python standard library; no external runtime dependencies

## Quick Example

```python
import azure.functions as func
from azure_functions_logging import setup_logging, get_logger, inject_context

# Initialize logging (usually at the module level or in a startup hook)
setup_logging()

logger = get_logger(__name__)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # Inject Azure Functions context into the logging system
    inject_context(context)

    logger.info("Processing request")

    # Context is automatically included in log output:
    # invocation_id, function_name, trace_id, cold_start
    return func.HttpResponse("Success", status_code=200)
```

### JSON Output (Production)

```python
setup_logging(format="json")

logger = get_logger(__name__)
logger.info("Processing request")
# {"timestamp": "2026-03-12T10:00:00Z", "level": "INFO", "logger": "...", "message": "Processing request", ...}
```

### Context Binding

```python
bound = logger.bind(user_id="abc", operation="checkout")
bound.info("Processing")
# Output includes user_id and operation in every log line
```

## Scope

This library is designed specifically for the **Azure Functions Python v2 programming model**. It relies on Python's standard `logging` module and does not introduce external dependencies for core functionality.

This package does **not** target distributed tracing, log aggregation pipelines, or OpenTelemetry integration. It focuses on making the logging experience better for developers writing Azure Functions in Python.

## Compatibility

- Python 3.10, 3.11, 3.12, 3.13, 3.14
- Azure Functions Python v2 programming model
- Works in both local development and Azure-hosted environments

## Next Steps

- [Installation](installation.md) -- How to add the package to your project
- [Usage Guide](usage.md) -- Detailed guide on all logging features
- [API Reference](api.md) -- Full documentation of classes and functions
- [Architecture](architecture.md) -- Internal design principles and module structure
- [Troubleshooting](troubleshooting.md) -- Common issues and solutions

## Project Links

- [Source Code](https://github.com/yeongseon/azure-functions-logging)
- [PyPI Package](https://pypi.org/project/azure-functions-logging/)
- [Issue Tracker](https://github.com/yeongseon/azure-functions-logging/issues)
- [Changelog](changelog.md)
- [Contributing](contributing.md)
