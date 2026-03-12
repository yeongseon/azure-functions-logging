# Azure Functions Logging

Developer-friendly logging helpers for Azure Functions Python.

Azure Functions Logging provides a thin wrapper around the standard Python `logging` module to make logging in Azure Functions more developer-friendly. It handles context injection, cold start detection, and provides clean, colorized output for local development and JSON formatting for production environments.

## Key Features

- **Colorized Output**: Clean, readable logs during local development.
- **JSON Formatting**: NDJSON output for production environments, compatible with Azure Log Analytics.
- **Context Injection**: Automatically include invocation IDs, function names, and trace IDs in every log line.
- **Cold Start Detection**: Automatically detect and flag cold starts in your logs.
- **Context Binding**: Bind additional key-value pairs to loggers for persistent context across multiple log calls.
- **Host Config Warning**: Automatically detect and warn about potential `host.json` logging level conflicts.

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
    
    logger.info("Processing request", user_id="123")
    
    # Context is automatically included in log output
    return func.HttpResponse("Success", status_code=200)
```

## Next Steps

- [Installation](installation.md): How to add the package to your project.
- [Usage Guide](usage.md): Detailed guide on how to use the logging features.
- [API Reference](api.md): Full documentation of classes and functions.
- [Architecture](architecture.md): Overview of design principles and internal structure.

## Scope

This library is designed specifically for the **Azure Functions Python v2 programming model**. It relies on the standard Python `logging` module and does not introduce external dependencies for core functionality.
