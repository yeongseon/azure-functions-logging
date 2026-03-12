# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-03-12

### Added

- `py.typed` marker file for PEP 561 type checking support, enabling downstream projects to use type information from this package with mypy, pyright, and other type checkers

## [0.2.0] - 2026-03-12

### Added

- `JsonFormatter` for structured NDJSON log output, compatible with Azure Log Analytics and other log aggregation systems
- `FunctionLogger` class with context binding via `bind()` for persistent per-request context
- Invocation context injection via `inject_context(context)`, automatically extracting `invocation_id`, `function_name`, and `trace_id` from the Azure Functions context object
- Automatic cold start detection without manual instrumentation -- first invocation per process is flagged as `cold_start=True`
- `host.json` log level conflict warning -- detects when Azure's host configuration might silently suppress log output
- `ContextFilter` for propagating context fields from `contextvars` to log records
- Translated README files: Korean, Japanese, Chinese

### Changed

- Expanded documentation with MkDocs site infrastructure (11 documentation pages)

## [0.1.0] - 2026-03-11

### Added

- `setup_logging()` one-liner for environment-aware log configuration with automatic Azure detection
- `get_logger(__name__)` helper for creating `FunctionLogger` instances from standard loggers
- `ColorFormatter` with colorized log levels for local development:
    - DEBUG: gray
    - INFO: blue
    - WARNING: yellow
    - ERROR: red
    - CRITICAL: bold red
- Clean `[TIME] [LEVEL] [LOGGER] message` format for human-readable output
- Exception-friendly output with readable stack traces
- Idempotent setup -- calling `setup_logging()` multiple times is safe
- Compatible with Python's standard `logging` module
- Support for Python 3.10, 3.11, 3.12, 3.13, 3.14

[0.2.1]: https://github.com/yeongseon/azure-functions-logging/releases/tag/v0.2.1
[0.2.0]: https://github.com/yeongseon/azure-functions-logging/releases/tag/v0.2.0
[0.1.0]: https://github.com/yeongseon/azure-functions-logging/releases/tag/v0.1.0
