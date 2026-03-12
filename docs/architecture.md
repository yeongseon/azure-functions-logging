# Architecture and Design

Understanding the internal design of Azure Functions Logging.

## Module Structure

The package is organized into several modules for clear separation of concerns:

- `src/azure_functions_logging/`
    - `__init__.py`: Public API exports (`setup_logging`, `get_logger`, `inject_context`).
    - `_setup.py`: Logic for configuring the logging system and environment detection.
    - `_logger.py`: Implementation of `FunctionLogger` and context binding logic.
    - `_context.py`: `contextvars` management and `ContextFilter` implementation.
    - `_json_formatter.py`: `JsonFormatter` implementation for NDJSON output.
    - `_formatter.py`: `ColorFormatter` implementation for local development.
    - `_host_config.py`: Logic to detect and warn about `host.json` conflicts.

## Design Principles

1. **Zero-config**: `setup_logging()` detects the environment automatically and adjusts its behavior.
2. **Non-invasive**: The library uses the standard `logging` module. It doesn't force a custom logger class hierarchy, ensuring compatibility with other libraries.
3. **Context propagation via contextvars**: Uses Python's `contextvars` to ensure thread-safe and async-safe context management.
4. **Silent failure**: Context injection (`inject_context`) never raises exceptions, even if the provided object is missing attributes.
5. **Idempotent setup**: Calling `setup_logging()` multiple times is safe and won't cause double-logging or configuration issues.

## Environment Detection

The library uses environment variables to detect if it's running in an Azure Functions environment:

- **FUNCTIONS_WORKER_RUNTIME**: Set to `python` in Azure.
- **WEBSITE_INSTANCE_ID**: Set in Azure environments.

If these are detected, the library assumes it's running in Azure and only adds a filter to the existing root logger handler, avoiding redundant setup.

## Context Flow

The flow of context from the function invocation to the log output:

1. **inject_context(context)**: Called in the Azure Functions handler.
2. **contextvars**: Stores the context fields (invocation_id, function_name, etc.) in the current task/thread.
3. **ContextFilter**: A logging filter that extracts fields from `contextvars` and attaches them to the `LogRecord`.
4. **LogRecord**: A standard Python object containing log message and metadata.
5. **Formatter**: (`JsonFormatter` or `ColorFormatter`) Reads the context fields from the `LogRecord` and formats the final output string.

## FunctionLogger Wrapper Pattern

The `FunctionLogger` class acts as a thin wrapper around the standard `logging.Logger`. This allows for additional functionality like `bind()` for persistent context without having to modify the global logging system or use a custom logger class that might break other libraries.
