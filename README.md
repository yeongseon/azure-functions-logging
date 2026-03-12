# azure-functions-logging

[![PyPI](https://img.shields.io/pypi/v/azure-functions-logging.svg)](https://pypi.org/project/azure-functions-logging/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-logging/)
[![CI](https://github.com/yeongseon/azure-functions-logging/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging/actions/workflows/ci-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Developer-friendly logging helpers for the **Azure Functions Python v2 programming model**.

## Why Use It

Azure Functions Python handlers share the same logging pain points:

- log output is visually dense and hard to scan
- errors do not stand out from info-level noise
- default formatting is not optimized for human readability

`azure-functions-logging` provides colorized, cleanly formatted log output that works with Python's standard `logging` module and requires minimal setup.

## Scope

- Azure Functions Python **v2 programming model**
- Python's standard `logging` module
- Colorized and JSON log output
- Invocation context injection and cold start detection

This package does **not** target distributed tracing, log aggregation, or OpenTelemetry integration.

## Features

- Colorized log levels (DEBUG gray, INFO blue, WARNING yellow, ERROR red, CRITICAL bold red)
- JSON structured log output for production and CI environments
- Clean `[TIME] [LEVEL] [LOGGER] message` format
- `setup_logging()` one-liner configuration
- `get_logger(__name__)` helper for convenient logger creation
- Automatic invocation context injection (invocation_id, function_name, trace_id)
- Cold start detection without manual instrumentation
- Context binding via `logger.bind(user_id="abc")`
- `host.json` log level conflict warning
- Exception-friendly output with readable stack traces
- Compatible with Python's standard `logging` module

## Installation

```bash
pip install azure-functions-logging
```

## Quick Start

```python
from azure_functions_logging import get_logger, setup_logging

setup_logging()

logger = get_logger(__name__)
logger.info("Processing request")
```

### JSON Output

```python
setup_logging(format="json")

logger = get_logger(__name__)
logger.info("Processing request")
# {"timestamp": "...", "level": "INFO", "logger": "...", "message": "Processing request", ...}
```

### Context Injection

```python
from azure_functions_logging import inject_context

def my_function(req, context):
    inject_context(context)
    logger.info("Handling request")  # includes invocation_id, function_name, trace_id
```

### Context Binding

```python
bound = logger.bind(user_id="abc", operation="checkout")
bound.info("Processing")  # includes user_id + operation in every log line
```

## Development

```bash
git clone https://github.com/yeongseon/azure-functions-logging.git
cd azure-functions-logging
pip install -e .[dev]
```

## Documentation

- Product requirements: `PRD.md`

## Disclaimer

This project is an independent community project and is not affiliated with,
endorsed by, or maintained by Microsoft.

Azure and Azure Functions are trademarks of Microsoft Corporation.

## License

MIT
