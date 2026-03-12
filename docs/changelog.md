# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2026-03-12

### Added
- Added: `py.typed` marker file for PEP 561 type checking support

## [0.2.0] - 2026-03-12

### Added
- Added: `JsonFormatter` for structured NDJSON log output
- Added: `FunctionLogger` class with context binding via `bind()`
- Added: Invocation context injection (invocation_id, function_name, trace_id)
- Added: Automatic cold start detection
- Added: `host.json` log level conflict warning
- Added: `ContextFilter` for propagating context fields to log records

## [0.1.0] - 2026-03-11

### Added
- Added: `setup_logging()` one-liner for environment-aware log configuration
- Added: `get_logger(__name__)` helper for convenient logger creation
- Added: `ColorFormatter` with colorized log levels (DEBUG gray, INFO blue, WARNING yellow, ERROR red, CRITICAL bold red)
- Added: Clean [TIME] [LEVEL] [LOGGER] message format
- Added: Exception-friendly output with readable stack traces
- Added: Compatible with Python's standard logging module
