# API Reference

Complete reference for all public classes and functions in `azure-functions-logging`.

## setup_logging

Initialize the logging system for your application.

```python
def setup_logging(
    *,
    level: int = logging.INFO,
    format: str = "color",
    logger_name: str | None = None,
) -> None
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `level` | `int` | `logging.INFO` | Standard logging level. Accepts `logging.DEBUG`, `logging.INFO`, `logging.WARNING`, `logging.ERROR`, `logging.CRITICAL`. |
| `format` | `str` | `"color"` | Output format. `"color"` for colorized terminal output, `"json"` for NDJSON structured output. |
| `logger_name` | `str \| None` | `None` | Name of the logger to configure. If `None`, configures the root logger. |

### Behavior

- **Idempotent**: Calling `setup_logging()` multiple times is safe. Only the first call takes effect.
- **Environment detection**: Automatically detects Azure Functions environments via `FUNCTIONS_WORKER_RUNTIME` and `WEBSITE_INSTANCE_ID` environment variables. In Azure, it only adds a `ContextFilter` to the existing handler to avoid duplicate log output.
- **Host config check**: Reads `host.json` (if present) to detect log level conflicts and emits a warning if the host configuration might suppress application-level logs.

### Examples

Basic setup with defaults (colorized INFO-level output):

```python
from azure_functions_logging import setup_logging

setup_logging()
```

Debug-level JSON output for production:

```python
import logging
from azure_functions_logging import setup_logging

setup_logging(level=logging.DEBUG, format="json")
```

Configure a specific logger instead of the root logger:

```python
setup_logging(logger_name="my_app")
```

---

## get_logger

Create a `FunctionLogger` instance wrapping a standard `logging.Logger`.

```python
def get_logger(name: str | None = None) -> FunctionLogger
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `name` | `str \| None` | `None` | Logger name. Typically `__name__` for module-level loggers. If `None`, returns a logger wrapping the root logger. |

### Returns

A `FunctionLogger` instance.

### Examples

```python
from azure_functions_logging import get_logger

# Module-level logger (recommended)
logger = get_logger(__name__)

# Root logger
root_logger = get_logger()
```

---

## FunctionLogger

A wrapper class around `logging.Logger` that adds context binding support. Created via `get_logger()`.

### Methods

#### bind

```python
def bind(**kwargs: Any) -> FunctionLogger
```

Returns a **new** `FunctionLogger` instance with additional bound context. The original logger is not modified. Bound context fields are included in every subsequent log call from the returned logger.

```python
logger = get_logger(__name__)

# Create a request-scoped logger with bound context
request_logger = logger.bind(user_id="abc-123", request_id="req-456")

request_logger.info("Processing")
# Output includes user_id="abc-123" and request_id="req-456"

# Original logger is unaffected
logger.info("Other message")
# Output does NOT include user_id or request_id
```

Binding is cumulative:

```python
l1 = logger.bind(user_id="abc")
l2 = l1.bind(session_id="xyz")

l2.info("message")
# Output includes both user_id="abc" and session_id="xyz"
```

#### clear_context

```python
def clear_context() -> None
```

Removes all bound context from the current logger instance.

```python
bound = logger.bind(user_id="abc")
bound.clear_context()
bound.info("message")
# Output no longer includes user_id
```

#### Logging Methods

`FunctionLogger` exposes the same logging methods as `logging.Logger`:

```python
logger.debug(msg, *args, **kwargs)      # Log at DEBUG level
logger.info(msg, *args, **kwargs)       # Log at INFO level
logger.warning(msg, *args, **kwargs)    # Log at WARNING level
logger.error(msg, *args, **kwargs)      # Log at ERROR level
logger.critical(msg, *args, **kwargs)   # Log at CRITICAL level
logger.exception(msg, *args, **kwargs)  # Log at ERROR level with traceback
```

Extra keyword arguments are included in the log output:

```python
logger.info("User action", action="login", ip="192.168.1.1")
```

#### Level Management

```python
logger.setLevel(level: int) -> None          # Set the logging level
logger.isEnabledFor(level: int) -> bool      # Check if level is enabled
logger.getEffectiveLevel() -> int            # Get the effective level
```

### Properties

| Property | Type | Description |
| -------- | ---- | ----------- |
| `name` | `str` | The name of the underlying logger |

---

## inject_context

Inject Azure Functions execution context into the logging system.

```python
def inject_context(context: Any) -> None
```

### Parameters

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `context` | `Any` | The Azure Functions context object (typically `func.Context`). Any object is accepted; missing attributes are silently ignored. |

### Behavior

Sets the following context fields for all subsequent logs in the current execution context (via `contextvars`):

| Field | Source | Type |
| ----- | ------ | ---- |
| `invocation_id` | `context.invocation_id` | `str \| None` |
| `function_name` | `context.function_name` | `str \| None` |
| `trace_id` | `context.trace_context.trace_id` | `str \| None` |
| `cold_start` | Automatic detection | `bool` |

### Cold Start Detection

The first call to `inject_context()` per Python process sets `cold_start=True`. All subsequent calls set `cold_start=False`. This happens automatically without manual instrumentation.

### Safety

- Never raises exceptions, even if `context` is `None` or missing expected attributes
- Missing attributes default to `None` in log output
- Safe to call in non-Azure environments (context fields will be `None`)

### Example

```python
import azure.functions as func
from azure_functions_logging import inject_context, get_logger

logger = get_logger(__name__)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    inject_context(context)

    logger.info("Processing request")
    # Log output includes: invocation_id, function_name, trace_id, cold_start

    return func.HttpResponse("OK")
```

---

## JsonFormatter

A `logging.Formatter` subclass that outputs log records as NDJSON (Newline Delimited JSON).

### Output Format

Each log record is written as a single-line JSON object:

```json
{
  "timestamp": "2026-03-12T10:00:00.000000Z",
  "level": "INFO",
  "logger": "my_module",
  "message": "Processing request",
  "invocation_id": "abc-123",
  "function_name": "HttpTrigger",
  "trace_id": "def-456",
  "cold_start": false,
  "extra": {
    "user_id": "usr-789"
  }
}
```

### Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `timestamp` | `str` | ISO 8601 formatted timestamp |
| `level` | `str` | Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `logger` | `str` | Logger name |
| `message` | `str` | Log message |
| `invocation_id` | `str \| null` | Azure Functions invocation ID (from context) |
| `function_name` | `str \| null` | Azure Functions function name (from context) |
| `trace_id` | `str \| null` | Distributed trace ID (from context) |
| `cold_start` | `bool \| null` | Whether this is a cold start invocation |
| `exception` | `str \| null` | Exception traceback (if present) |
| `extra` | `object` | Additional fields from bound context or extra kwargs |

### Usage

```python
setup_logging(format="json")
```

The `JsonFormatter` is selected automatically when `format="json"` is passed to `setup_logging()`. You do not need to instantiate it directly.

---

## ColorFormatter

A `logging.Formatter` subclass that produces colorized terminal output for local development.

### Output Format

```
HH:MM:SS LEVEL logger message [context_fields]
```

### Color Mapping

| Level | Color |
| ----- | ----- |
| DEBUG | Gray |
| INFO | Blue |
| WARNING | Yellow |
| ERROR | Red |
| CRITICAL | Bold Red |

### TTY Detection

`ColorFormatter` automatically detects whether the output stream is a terminal (TTY). If the output is redirected or piped, ANSI color codes are omitted and plain text is output instead.

### Usage

```python
setup_logging(format="color")  # This is the default
```

---

## ContextFilter

A `logging.Filter` subclass that extracts context from `contextvars` and attaches it to log records.

### Context Fields

| Field | Description |
| ----- | ----------- |
| `invocation_id` | Azure Functions invocation ID |
| `function_name` | Azure Functions function name |
| `trace_id` | Distributed trace ID |
| `cold_start` | Cold start boolean flag |

### Behavior

The filter reads context values set by `inject_context()` from `contextvars` and adds them as attributes on each `LogRecord`. This makes the fields available to any formatter attached to the handler.

The filter never raises exceptions. Missing context fields default to `None`.

### Usage

`ContextFilter` is added automatically by `setup_logging()`. You do not need to add it manually unless you are building a custom logging configuration.
