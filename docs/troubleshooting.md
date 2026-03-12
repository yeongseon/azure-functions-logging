# Troubleshooting

Common issues and solutions for `azure-functions-logging`.

## No colored output in terminal

If logs aren't colorized, check if your `stdout` or `stderr` is a TTY.

The `ColorFormatter` automatically detects terminal capability. If the output is redirected or piped, colorization is disabled. Note that Azure Functions logging may redirect output, which could result in plain text logs.

## Logs not appearing

The `host.json` configuration for your Azure Functions App can override library settings.

Check the `logLevel.default` setting in your `host.json`. If this is set to a higher level (e.g., `Error`) than your logger's level (e.g., `Info`), logs will be suppressed. The library will emit a warning if a conflict is detected.

## Context fields are None

To include Azure Functions context in your logs, ensure `inject_context()` is called correctly.

You must pass the Azure Functions `context` object as an argument. If it's omitted or incorrect, the invocation ID, function name, and trace ID fields will remain `None`.

## setup_logging() called but no effect

The `setup_logging()` function is idempotent.

Only the first call to `setup_logging()` takes effect. Subsequent calls will not change the configuration to prevent multiple initializations. This ensures a consistent logging environment across your application.

## JSON output includes extra fields

The `JsonFormatter` includes all extra fields from the log record in the `extra` key.

Any attributes present in `record.__dict__` that are not part of the standard log record schema are automatically included in the structured output. This behavior ensures that no data is lost during the formatting process.

## Cold start always False

The `cold_start` flag is `True` only on the very first invocation per process.

Subsequent invocations within the same warm process will have `cold_start` set to `False`. If you're testing locally with the Azure Functions Core Tools, restarting the host will reset the cold start flag.
