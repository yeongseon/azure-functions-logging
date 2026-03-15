# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-03-15

### Added

- `SamplingFilter` for probabilistic log sampling
- `RedactionFilter` for masking sensitive fields in log records
- `ColorFormatter` `include_extra` parameter for structured extra fields in dev output
- `functions_formatter` parameter in `setup_logging()` for custom Azure handler formatting
- `host.json` `None` log level support (`logLevel.default: none`)
- Context leak reset between invocations (`invocation_id` and `function_name` cleared on re-entry)

### Fixed

- NDJSON output line-break handling in `JsonFormatter`

## [0.2.2] - 2026-03-14

### Added

- Unified tooling: Ruff (lint + format), pre-commit hooks, standardized Makefile
- Comprehensive documentation overhaul (17 MkDocs pages)
- 5 runnable example scripts with smoke tests
- Translated README files (Korean, Japanese, Chinese)
- Standardized nav structure and documentation quality across ecosystem
- pyproject.toml metadata (classifiers, project URLs)
- Project metadata in logging output

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
