# Troubleshooting

Common issues and solutions for `azure-functions-logging`.

## No Colored Output in Terminal

**Symptom**: Log output appears as plain text without colors.

**Cause**: The `ColorFormatter` automatically detects terminal capability. Colors are disabled when `stdout` or `stderr` is not a TTY (terminal).

**Common scenarios where colors are disabled**:

- Output is piped to another command (`python app.py | grep error`)
- Output is redirected to a file (`python app.py > log.txt`)
- Running inside a CI environment that does not support ANSI escape codes
- Azure Functions runtime redirects output internally

**Solution**: Colors are primarily a local development feature. In production or CI environments, use JSON formatting instead:

```python
setup_logging(format="json")
```

## Logs Not Appearing

**Symptom**: Logs are written in code but do not appear in the Azure Functions output.

**Cause 1: host.json log level override**

The `host.json` configuration for your Azure Functions App can override application-level log settings. If `logLevel.default` is set to a higher level than your logger's level, logs are silently suppressed.

Example `host.json` that suppresses INFO logs:

```json
{
  "logging": {
    "logLevel": {
      "default": "Warning"
    }
  }
}
```

The library detects this conflict and emits a warning. Check your terminal output for messages like:

```
WARNING: host.json logLevel 'Warning' may suppress logs at level 'INFO'
```

**Solution**: Adjust your `host.json` to match your desired log level, or set a specific override for your function:

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

**Cause 2: Logger name mismatch**

If you create a logger with a specific name but configure logging on a different logger, logs may not be captured.

**Solution**: Use `get_logger(__name__)` consistently throughout your modules. Call `setup_logging()` without a `logger_name` to configure the root logger (which captures all child loggers).

**Cause 3: Log level too high**

The default log level is `logging.INFO`. DEBUG-level messages will not appear unless you explicitly lower the level:

```python
import logging
setup_logging(level=logging.DEBUG)
```

## Context Fields Are None

**Symptom**: Log output shows `invocation_id=None`, `function_name=None`, `trace_id=None`.

**Cause**: `inject_context()` was not called, or was called with an object that does not have the expected attributes.

**Solution**: Call `inject_context(context)` at the beginning of each function handler, passing the Azure Functions `context` object:

```python
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    inject_context(context)  # Must be called before logging
    logger.info("Processing request")
    return func.HttpResponse("OK")
```

The `context` object must have these attributes:

- `invocation_id` (str)
- `function_name` (str)
- `trace_context.trace_id` (str)

If any attribute is missing, that field defaults to `None` without raising an error.

## setup_logging() Called but No Effect

**Symptom**: Calling `setup_logging()` does not change the logging behavior.

**Cause**: `setup_logging()` is idempotent. Only the first call configures the logging system. Subsequent calls are no-ops.

**Solution**: Ensure `setup_logging()` is called before any logging occurs, typically at module level or in an application startup hook:

```python
# At the top of your main module, before any logging
from azure_functions_logging import setup_logging
setup_logging()
```

If you need to change the configuration after setup, you must reconfigure the root logger manually using Python's standard `logging` module.

## JSON Output Includes Extra Fields

**Symptom**: JSON log output contains unexpected fields in the `extra` key.

**Cause**: The `JsonFormatter` includes all extra fields from the `LogRecord` in the JSON output. Any attributes present in `record.__dict__` that are not part of the standard log record schema are automatically included.

**Common sources of extra fields**:

- `logger.info("message", extra={"key": "value"})` -- explicit extra fields
- `logger.bind(user_id="abc").info("message")` -- bound context
- Third-party libraries that add custom attributes to log records

**Solution**: This is intentional behavior to ensure no data is lost. If you want to filter specific fields, create a custom formatter that inherits from `JsonFormatter` and overrides the formatting logic.

## Cold Start Always False

**Symptom**: The `cold_start` field is always `False` in log output.

**Cause**: The `cold_start` flag is `True` only on the very first invocation per Python process. All subsequent invocations within the same warm process have `cold_start=False`.

**Solution**: This is expected behavior. Cold starts are relatively infrequent in production. To observe a cold start locally:

1. Start the Azure Functions Core Tools host: `func start`
2. Send the first request -- this invocation will have `cold_start=True`
3. Send subsequent requests -- these will have `cold_start=False`
4. Restart the host to reset the cold start flag

## Double Logging (Duplicate Output)

**Symptom**: Each log message appears twice in the output.

**Cause**: Multiple handlers are attached to the logger. This can happen when:

- `setup_logging()` is called in a non-standard way that bypasses the idempotency check
- Another library or framework adds its own handler to the root logger
- The `logging.basicConfig()` function is called before or after `setup_logging()`

**Solution**:

1. Call `setup_logging()` once, as early as possible in your application
2. Do not call `logging.basicConfig()` in the same application
3. Check for conflicting logging configuration in other libraries

To verify the number of handlers on the root logger:

```python
import logging
print(len(logging.root.handlers))  # Should be 1 after setup_logging()
```

## Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'azure_functions_logging'`

**Cause**: The package is not installed in the current Python environment.

**Solution**:

1. Verify installation:

   ```bash
   pip show azure-functions-logging
   ```

2. If not installed, install it:

   ```bash
   pip install azure-functions-logging
   ```

3. If using a virtual environment, ensure it is activated before running your application.

4. For Azure Functions deployments, ensure `azure-functions-logging` is listed in your `requirements.txt`.

## Getting Help

If your issue is not covered here:

1. Check the [API Reference](api.md) for correct function signatures and parameters
2. Check the [Usage Guide](usage.md) for example code
3. Open an issue on [GitHub](https://github.com/yeongseon/azure-functions-logging/issues) with:
   - The code that produces the unexpected behavior
   - The actual output vs. expected output
   - Your Python version (`python --version`)
   - Your `azure-functions-logging` version (`pip show azure-functions-logging`)
   - Whether you are running locally or in Azure
