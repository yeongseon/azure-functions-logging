from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import sys

from azure_functions_logging._json_formatter import JsonFormatter


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


def test_basic_json_output_is_valid_and_has_expected_fields() -> None:
    formatter = JsonFormatter()
    record = _make_record(logging.INFO, "basic message")

    output = formatter.format(record)
    payload = json.loads(output)

    assert output.endswith("\n")
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    assert payload["message"] == "basic message"
    assert payload["invocation_id"] is None
    assert payload["function_name"] is None
    assert payload["trace_id"] is None
    assert payload["cold_start"] is None
    assert payload["exception"] is None
    assert payload["extra"] == {}


def test_context_fields_included_when_present() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="with context")
    record.invocation_id = "inv-1"
    record.function_name = "fn-1"
    record.trace_id = "trace-1"

    payload = json.loads(formatter.format(record))

    assert payload["invocation_id"] == "inv-1"
    assert payload["function_name"] == "fn-1"
    assert payload["trace_id"] == "trace-1"


def test_cold_start_field_for_true_false_and_none() -> None:
    formatter = JsonFormatter()

    record_true = _make_record(msg="cold")
    record_true.cold_start = True
    assert json.loads(formatter.format(record_true))["cold_start"] is True

    record_false = _make_record(msg="warm")
    record_false.cold_start = False
    assert json.loads(formatter.format(record_false))["cold_start"] is False

    record_none = _make_record(msg="none")
    record_none.cold_start = None
    assert json.loads(formatter.format(record_none))["cold_start"] is None


def test_exception_info_is_formatted_in_exception_field() -> None:
    formatter = JsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        record = _make_record(logging.ERROR, "failed")
        record.exc_info = sys.exc_info()

    payload = json.loads(formatter.format(record))

    assert payload["exception"] is not None
    assert "Traceback" in payload["exception"]
    assert "ValueError: boom" in payload["exception"]


def test_bound_context_is_collected_in_extra_field() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="bound")
    record.user_id = "abc"
    record.request_id = "req-1"
    record.invocation_id = "inv-1"

    payload = json.loads(formatter.format(record))

    assert payload["extra"] == {"request_id": "req-1", "user_id": "abc"}


def test_timestamp_is_iso8601_with_timezone() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="time")
    record.created = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc).timestamp()

    payload = json.loads(formatter.format(record))
    parsed = datetime.fromisoformat(payload["timestamp"])

    assert parsed.tzinfo is not None
    assert parsed.utcoffset() == timezone.utc.utcoffset(parsed)
