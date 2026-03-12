# Development

This guide explains how to set up your environment for developing and contributing to `azure-functions-logging`.

## Prerequisites

To get started, ensure you have the following installed:

* Python 3.10 or higher
* Git

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/yeongseon/azure-functions-logging.git
   cd azure-functions-logging
   ```

2. Install the package in editable mode with development dependencies:

   ```bash
   pip install -e .[dev]
   ```

## Project Structure

The project follows the standard `src` layout:

* `src/`: Contains the core library source code.
* `tests/`: Contains the test suite.
* `pyproject.toml`: Project configuration for build and tools.
* `Makefile`: Task automation for development workflows.

## Development Tasks

The project includes a `Makefile` to automate common development tasks.

| Command | Description |
|---------|-------------|
| `make format` | Format code with ruff and black |
| `make style` | Lint with ruff |
| `make typecheck` | Type check with mypy |
| `make lint` | Run both style and typecheck |
| `make test` | Run tests with pytest |
| `make cov` | Run tests and generate coverage report |
| `make security` | Run bandit security scan |
| `make check-all` | Run full local gate (lint, typecheck, security, tests) |

## Environment Management

This project uses Hatch as the build system and environment manager. Hatch handles virtual environments and dependency isolation automatically.

While you can use standard `pip` commands, you can also run development tasks via Hatch:

```bash
hatch run test
hatch run lint:all
```

## Pre-commit Hooks

To maintain code quality and consistency, the project uses pre-commit hooks. Install them to run automatically before every commit:

```bash
pre-commit install
```

!!! note
    Running `make check-all` before pushing your changes is highly recommended to ensure all CI checks will pass.
