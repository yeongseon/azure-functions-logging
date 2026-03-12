# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.1] - 2026-03-12

### Added

- `py.typed` marker file for PEP 561 type checking support

## [0.2.0] - 2026-03-12

### Added

- `JsonFormatter` for structured NDJSON log output
- `FunctionLogger` class with context binding via `bind()`
- Invocation context injection (invocation_id, function_name, trace_id)
- Automatic cold start detection
- `host.json` log level conflict warning
- `ContextFilter` for propagating context fields to log records

## [0.1.0] - 2026-03-11

### Added

- `setup_logging()` one-liner for environment-aware log configuration
- `get_logger(__name__)` helper for convenient logger creation
- `ColorFormatter` with colorized log levels (DEBUG gray, INFO blue, WARNING yellow, ERROR red, CRITICAL bold red)
- Clean `[TIME] [LEVEL] [LOGGER] message` format
- Exception-friendly output with readable stack traces
- Compatible with Python's standard `logging` module
