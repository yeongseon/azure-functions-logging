# Architecture and Design

This document describes the internal architecture, module structure, and design principles of `azure-functions-logging`.

## Module Structure

The package is organized into focused modules with clear separation of concerns:

```
src/azure_functions_logging/
+-- __init__.py          # Public API exports (setup_logging, get_logger, inject_context)
+-- _setup.py            # Logging system configuration and environment detection
+-- _logger.py           # FunctionLogger implementation and context binding
+-- _context.py          # contextvars management and ContextFilter
+-- _json_formatter.py   # JsonFormatter for NDJSON output
+-- _formatter.py        # ColorFormatter for local development
+-- _host_config.py      # host.json conflict detection and warnings
+-- py.typed             # PEP 561 marker for type checking support
```

### Module Responsibilities

**`__init__.py`** -- Public API surface. Exports `setup_logging`, `get_logger`, `inject_context`, `FunctionLogger`, and `JsonFormatter`. Contains the `get_logger()` factory function that wraps `logging.getLogger()` with a `FunctionLogger` instance.

**`_setup.py`** -- Entry point for logging configuration. Handles environment detection (Azure vs. local), creates formatters and handlers, configures the root logger, and ensures idempotent setup. This module decides whether to attach a full handler (local) or just a filter (Azure).

**`_logger.py`** -- Implements `FunctionLogger`, a thin wrapper around `logging.Logger` that adds context binding via `bind()`. The wrapper pattern avoids modifying the global logging system or requiring a custom logger class that might break compatibility with other libraries.

**`_context.py`** -- Manages context propagation using Python's `contextvars` module. Implements `inject_context()` to extract invocation ID, function name, and trace ID from the Azure Functions context object. Implements `ContextFilter`, a `logging.Filter` subclass that reads context values from `contextvars` and attaches them to `LogRecord` objects.

**`_json_formatter.py`** -- Implements `JsonFormatter`, a `logging.Formatter` subclass that outputs NDJSON (Newline Delimited JSON). Each log record becomes a single-line JSON object with timestamp, level, logger name, message, context fields, exception info, and any extra fields.

**`_formatter.py`** -- Implements `ColorFormatter`, a `logging.Formatter` subclass that produces colorized terminal output. Maps log levels to ANSI color codes (DEBUG gray, INFO blue, WARNING yellow, ERROR red, CRITICAL bold red). Automatically detects terminal capability and disables colors when output is redirected.

**`_host_config.py`** -- Reads the `host.json` file (if present) to detect logging level conflicts. Azure Functions' `host.json` can override application-level log settings, silently suppressing log output. This module warns developers when it detects a mismatch.

## Design Principles

### Zero-Config

`setup_logging()` detects the environment automatically and adjusts its behavior. No configuration is required for the common case. The function accepts optional parameters for customization, but sensible defaults cover most use cases.

### Non-Invasive

The library uses Python's standard `logging` module exclusively. It does not force a custom logger class hierarchy, monkey-patch the logging system, or introduce proprietary log handling. This ensures compatibility with any library that uses standard Python logging.

### Context Propagation via contextvars

Context fields (invocation ID, function name, trace ID, cold start) are stored using Python's `contextvars` module. This provides thread-safe and async-safe context management without requiring developers to pass context objects through their call stack.

The flow:

1. `inject_context(context)` is called in the Azure Functions handler
2. Context fields are stored in `contextvars` for the current execution context
3. `ContextFilter` reads the fields from `contextvars` for each log record
4. The formatter (JSON or Color) includes the context fields in the output

### Silent Failure

`inject_context()` never raises exceptions, even if the provided object is missing expected attributes. This defensive approach prevents logging setup from crashing the application. Missing attributes result in `None` values in the log output.

### Idempotent Setup

Calling `setup_logging()` multiple times is safe. Only the first call configures the logging system. Subsequent calls are no-ops. This prevents double-logging, duplicate handlers, and configuration conflicts when multiple modules or initialization paths call `setup_logging()`.

## Environment Detection

The library uses environment variables to detect whether it is running in an Azure Functions environment:

- **`FUNCTIONS_WORKER_RUNTIME`**: Set to `python` in Azure Functions
- **`WEBSITE_INSTANCE_ID`**: Set in Azure App Service / Functions environments

### Azure Environment Behavior

When running in Azure, the Azure Functions host already configures logging handlers. Adding another handler would cause duplicate log output. In this case, `setup_logging()` only adds a `ContextFilter` to the existing root logger handler. This attaches context fields to log records without duplicating log output.

### Local Environment Behavior

When running locally (no Azure environment variables detected), `setup_logging()` sets up a full handler with the selected formatter (`ColorFormatter` or `JsonFormatter`). This provides readable, formatted output for local development and testing.

## Context Flow Diagram

```
Azure Functions Handler
        |
        v
inject_context(context)
        |
        v
contextvars (thread-local storage)
   - invocation_id
   - function_name
   - trace_id
   - cold_start
        |
        v
ContextFilter (logging.Filter)
   reads from contextvars
   attaches to LogRecord
        |
        v
Formatter (JsonFormatter or ColorFormatter)
   reads from LogRecord
   formats output string
        |
        v
Handler (StreamHandler)
   writes to stdout/stderr
```

## FunctionLogger Wrapper Pattern

The `FunctionLogger` class wraps a standard `logging.Logger` rather than subclassing it. This design choice has several benefits:

- **Compatibility**: Other libraries that interact with the logging system see a standard `logging.Logger`. No custom metaclass registration or logger class replacement is needed.
- **Immutable binding**: `bind()` returns a new `FunctionLogger` instance with the additional context, leaving the original logger unchanged. This makes it safe to create request-scoped loggers without affecting other parts of the application.
- **Standard interface**: `FunctionLogger` exposes the same methods as `logging.Logger` (debug, info, warning, error, critical, exception, setLevel, isEnabledFor, getEffectiveLevel). Code using `FunctionLogger` can be switched to a standard logger without changes.

## Cold Start Detection

Cold start detection is implemented at the module level using a global boolean flag:

1. On module import, a flag is set to `True`
2. The first call to `inject_context()` checks the flag, sets `cold_start=True` in the context, and flips the flag to `False`
3. All subsequent calls to `inject_context()` set `cold_start=False`

This approach works because Azure Functions reuses the same Python process for multiple invocations. The first invocation after process startup is the cold start. No external state or timing logic is needed.

## Error Handling Philosophy

The library follows a "never crash the application" approach:

- `inject_context()` catches `AttributeError` when accessing context fields and defaults to `None`
- `setup_logging()` catches configuration errors and falls back to basic logging
- `ContextFilter` never raises during filtering; missing context fields default to `None`
- `host.json` reading catches file I/O errors and JSON parse errors silently

This is appropriate for a logging library because a failure in logging should never prevent the application from doing its primary work.
