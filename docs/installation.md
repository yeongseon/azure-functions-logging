# Installation

Installing Azure Functions Logging is simple and requires only Python 3.10 or higher.

## Using pip

The easiest way to install the package is via `pip`:

```bash
pip install azure-functions-logging
```

## Adding to Requirements

For Azure Functions projects, add the package to your `requirements.txt` file to ensure it's available in the deployment environment:

```text
# requirements.txt
azure-functions
azure-functions-logging==0.2.1
```

## Development Installation

If you want to contribute to the project or run tests locally, you can install the package in editable mode with development dependencies:

```bash
git clone https://github.com/yeongseon/azure-functions-logging.git
cd azure-functions-logging
pip install -e .[dev]
```

## Prerequisites

- **Python Version**: >=3.10
- **External Dependencies**: None (this package only uses the Python standard library).

!!! note
    While this package is designed for Azure Functions, it will also work in local environments for testing. It automatically detects if it's running in an Azure environment to adjust its behavior.
