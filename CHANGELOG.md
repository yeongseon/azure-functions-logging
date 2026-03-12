# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.0] - 2026-03-11

### Added

- `setup_logging()` one-liner for environment-aware log configuration
- `get_logger(__name__)` helper for convenient logger creation
- `ColorFormatter` with colorized log levels (DEBUG gray, INFO blue, WARNING yellow, ERROR red, CRITICAL bold red)
- Clean `[TIME] [LEVEL] [LOGGER] message` format
- Exception-friendly output with readable stack traces
- Compatible with Python's standard `logging` module
