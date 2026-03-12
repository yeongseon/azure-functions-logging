# Testing

This guide covers the testing strategy, structure, and practices for `azure-functions-logging`.

## Running Tests

### All Tests

```bash
make test
```

Or using Hatch:

```bash
hatch run test
```

Both commands run the full test suite via pytest.

### With Coverage

```bash
make cov
```

Or:

```bash
hatch run cov
```

This generates a coverage report showing line-by-line coverage for the entire package.

### Specific Test File

```bash
pytest tests/test_formatter.py
```

### Tests Matching a Pattern

```bash
pytest -k "test_json"
```

### Verbose Output

```bash
pytest -v tests/
```

## Test Structure

All tests reside in the `tests/` directory:

```
tests/
+-- test_logging.py      # Logging setup and configuration tests
+-- test_formatter.py     # ColorFormatter and JsonFormatter tests
+-- test_context.py       # Context injection, binding, and ContextFilter tests
```

### test_logging.py

Tests for the `setup_logging()` function and overall logging system configuration:

- Default setup creates a handler with `ColorFormatter`
- `format="json"` creates a handler with `JsonFormatter`
- Idempotent setup (multiple calls do not add duplicate handlers)
- Custom log level configuration
- Logger name targeting
- Environment detection (Azure vs. local)
- Host.json conflict detection and warning

### test_formatter.py

Tests for both `ColorFormatter` and `JsonFormatter`:

**ColorFormatter tests**:

- Format string structure: `HH:MM:SS LEVEL logger message`
- Color codes per level (DEBUG gray, INFO blue, WARNING yellow, ERROR red, CRITICAL bold red)
- TTY detection (colors disabled when output is not a terminal)
- Exception formatting with readable stack traces
- Extra fields included in output

**JsonFormatter tests**:

- Output is valid JSON (single line per record)
- All required fields present: timestamp, level, logger, message
- Context fields included when set: invocation_id, function_name, trace_id, cold_start
- Extra fields from `bind()` and keyword arguments included in `extra` object
- Exception traceback included in `exception` field
- Timestamp format is ISO 8601

### test_context.py

Tests for context injection, binding, and the ContextFilter:

**inject_context tests**:

- Extracts invocation_id, function_name, trace_id from context object
- Cold start detection (first call returns True, subsequent calls return False)
- Handles missing attributes gracefully (defaults to None)
- Handles None context without raising
- Thread safety via contextvars

**FunctionLogger.bind tests**:

- Bound context is included in log output
- Binding is immutable (original logger is not modified)
- Cumulative binding (bind on a bound logger combines both contexts)
- clear_context removes all bound fields

**ContextFilter tests**:

- Filter attaches context fields to LogRecord
- Filter works with no context set (fields default to None)
- Filter does not raise on any input

## Writing Tests

### Test File Naming

Test files follow the `test_*.py` naming convention. Each test file corresponds to a logical area of the library.

### Test Function Naming

Use descriptive names that explain the expected behavior:

```python
def test_setup_logging_with_json_format_creates_json_formatter():
    ...

def test_inject_context_with_missing_attributes_defaults_to_none():
    ...

def test_cold_start_is_true_only_on_first_invocation():
    ...
```

### Test Structure

```python
import logging
import pytest
from azure_functions_logging import setup_logging, get_logger, inject_context

def test_basic_logging_setup():
    """setup_logging() configures the root logger with a handler."""
    # Arrange
    setup_logging()

    # Act
    logger = get_logger(__name__)
    logger.info("test message")

    # Assert
    root = logging.getLogger()
    assert len(root.handlers) >= 1
```

### Testing Context

When testing context injection, create a mock context object:

```python
class MockContext:
    invocation_id = "test-invocation-id"
    function_name = "TestFunction"

    class trace_context:
        trace_id = "test-trace-id"

def test_inject_context_sets_fields():
    inject_context(MockContext())
    logger = get_logger(__name__)
    # Verify context fields appear in output
```

### Testing Formatters

Capture log output using a `StringIO` handler:

```python
import io
import logging

def test_json_formatter_output():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("test")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("test message")

    output = stream.getvalue()
    data = json.loads(output)
    assert data["message"] == "test message"
    assert data["level"] == "INFO"
```

## CI Test Matrix

Tests run automatically on every pull request and push to `main`. The CI matrix covers:

| Python Version | Status |
| -------------- | ------ |
| 3.10 | Tested |
| 3.11 | Tested |
| 3.12 | Tested |
| 3.13 | Tested |
| 3.14 | Tested |

All tests must pass across the entire matrix before a pull request can be merged.

## Coverage

Coverage is tracked via pytest-cov and reported to Codecov. The current coverage badge is visible in the project README.

To check coverage locally:

```bash
make cov
```

The report shows:

- Line coverage per module
- Branch coverage per module
- Uncovered lines highlighted

When adding new features, ensure coverage does not decrease. New code should have corresponding test coverage.

## Test Best Practices

- **Isolate tests**: Each test should be independent and not rely on state from other tests
- **Clean up**: Reset logging handlers and contextvars after tests to avoid interference
- **Use fixtures**: Leverage pytest fixtures for common setup (mock contexts, loggers, handlers)
- **Test edge cases**: Missing attributes, None values, empty strings, concurrent access
- **Test the public API**: Focus on testing through `setup_logging()`, `get_logger()`, and `inject_context()` rather than internal implementations
- **Regression tests**: Every bug fix must include a test that would have caught the bug
