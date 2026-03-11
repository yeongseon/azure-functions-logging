from __future__ import annotations

import logging
import sys

from azure_functions_logging._formatter import ColorFormatter


def _make_record(level: int = logging.INFO, msg: str = "hello") -> logging.LogRecord:
    return logging.LogRecord(
        name="test.logger",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )


def test_basic_format_output_contains_time_level_name_message() -> None:
    formatter = ColorFormatter()
    record = _make_record(logging.INFO, "basic message")

    output = formatter.format(record)

    assert "test.logger" in output
    assert "basic message" in output
    assert "INFO" in output


def test_context_fields_appended_when_present() -> None:
    formatter = ColorFormatter()
    record = _make_record(msg="with context")
    record.invocation_id = "inv-1"
    record.function_name = "fn-1"
    record.trace_id = "trace-1"

    output = formatter.format(record)

    assert "invocation_id=inv-1" in output
    assert "function_name=fn-1" in output
    assert "trace_id=trace-1" in output


def test_cold_start_shown_only_when_true() -> None:
    formatter = ColorFormatter()
    record_true = _make_record(msg="cold")
    record_true.cold_start = True

    output_true = formatter.format(record_true)
    assert "cold_start=true" in output_true

    record_false = _make_record(msg="warm")
    record_false.cold_start = False
    output_false = formatter.format(record_false)
    assert "cold_start=true" not in output_false

    record_none = _make_record(msg="none")
    record_none.cold_start = None
    output_none = formatter.format(record_none)
    assert "cold_start=true" not in output_none


def test_exception_info_is_included() -> None:
    formatter = ColorFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="failed",
            args=(),
            exc_info=None,
        )
        record.exc_info = sys.exc_info()

    output = formatter.format(record)

    assert "Traceback" in output
    assert "ValueError: boom" in output


def test_is_tty_returns_bool() -> None:
    result = ColorFormatter.is_tty()
    assert isinstance(result, bool)
