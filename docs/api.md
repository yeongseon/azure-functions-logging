# API Reference

Detailed information on the classes and functions provided by Azure Functions Logging.

## `setup_logging`

Initialize logging for your application.

```python
def setup_logging(
    *, 
    level: int = logging.INFO, 
    format: str = "color", 
    logger_name: str | None = None
) -> None
```

- **level**: Standard logging level (e.g., `logging.DEBUG`, `logging.INFO`). Defaults to `logging.INFO`.
- **format**: Either `"color"` for terminal-friendly output or `"json"` for NDJSON output. Defaults to `"color"`.
- **logger_name**: The name of the logger to configure. If `None`, it configures the root logger.

!!! note
    This function is idempotent and can be called multiple times without any side effects.

## `get_logger`

Get a `FunctionLogger` instance.

```python
def get_logger(name: str | None = None) -> FunctionLogger
```

- **name**: The name of the logger. If `None`, it returns a logger with no name (root).

## `FunctionLogger`

A wrapper class for the standard `logging.Logger` that adds context binding support.

### Methods

- **`bind(**kwargs) -> FunctionLogger`**: Returns a new `FunctionLogger` instance with additional bound context. This is an immutable operation.
- **`clear_context() -> None`**: Clear all bound context from the current logger instance.
- **`debug(msg, *args, **kwargs)`**: Log a message at DEBUG level.
- **`info(msg, *args, **kwargs)`**: Log a message at INFO level.
- **`warning(msg, *args, **kwargs)`**: Log a message at WARNING level.
- **`error(msg, *args, **kwargs)`**: Log a message at ERROR level.
- **`critical(msg, *args, **kwargs)`**: Log a message at CRITICAL level.
- **`exception(msg, *args, **kwargs)`**: Log a message at ERROR level with exception traceback.
- **`setLevel(level: int)`**: Set the logging level for this logger.
- **`isEnabledFor(level: int) -> bool`**: Check if the logger is enabled for a specific level.
- **`getEffectiveLevel() -> int`**: Get the effective logging level for this logger.

### Properties

- **`name`**: The name of the logger.

## `inject_context`

Inject the Azure Functions `context` into the logging system.

```python
def inject_context(context: Any) -> None
```

Sets the following fields for all subsequent logs in the current execution context:
- `invocation_id`
- `function_name`
- `trace_id`
- `cold_start` (boolean)

!!! note
    It's safe to call this with any object; it will silently ignore missing attributes.

## `JsonFormatter`

A `logging.Formatter` subclass that outputs NDJSON.

- **Output Format**: Each log record is written as a single-line JSON object.
- **Fields**: `timestamp`, `level`, `logger`, `message`, `invocation_id`, `function_name`, `trace_id`, `cold_start`, `exception`, and any `extra` fields.

## `ColorFormatter`

A `logging.Formatter` subclass for colorized terminal output.

- **Format**: `"HH:MM:SS LEVEL logger message [context_fields]"`
- **Colors**:
    - DEBUG: Gray
    - INFO: Blue
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Bold Red

## `ContextFilter`

A `logging.Filter` subclass that extracts context from `contextvars`.

- **CONTEXT_FIELDS**: `invocation_id`, `function_name`, `trace_id`, `cold_start`.
