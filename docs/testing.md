# Testing

`azure-functions-logging` prioritizes reliability and correctness through a comprehensive test suite.

## Running Tests

You can run the test suite using either `make` or `hatch`:

```bash
# Using make
make test

# Using hatch
hatch run test
```

## Coverage Reports

To check code coverage and ensure new features are well-tested:

```bash
# Using make
make cov

# Using hatch
hatch run cov
```

## Test Structure

All tests reside in the `tests/` directory at the root of the repository. The test suite is organized into several modules:

* `tests/test_logging.py`: Tests for basic logging setup and configuration.
* `tests/test_formatter.py`: Tests for color and JSON formatters.
* `tests/test_context.py`: Tests for context injection and binding.

## Writing New Tests

New features should always include corresponding tests. The project uses `pytest` for testing.

1. Follow the naming convention: `test_*.py` for test files and `test_*` for test functions.
2. Use descriptive names for your test functions.
3. Leverage standard `pytest` features like fixtures and parametrization.

!!! note
    Refer to existing tests in the `tests/` directory for implementation patterns.

## CI Environment

Tests are executed automatically on every pull request and push to the main branch. The CI matrix covers a range of Python versions:

* Python 3.10
* Python 3.11
* Python 3.12
* Python 3.13
* Python 3.14

!!! warning
    Pull requests will not be merged until all tests pass across the entire Python version matrix.
