"""Tests for SamplingFilter and RedactionFilter."""

from __future__ import annotations

import logging
import time

import pytest

from azure_functions_logging._filters import RedactionFilter, SamplingFilter


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


# ---------------------------------------------------------------------------
# SamplingFilter tests
# ---------------------------------------------------------------------------


def test_sampling_filter_passes_records_within_rate() -> None:
    flt = SamplingFilter(rate=3, window=10.0)
    for _ in range(3):
        assert flt.filter(_make_record()) is True


def test_sampling_filter_drops_records_beyond_rate() -> None:
    flt = SamplingFilter(rate=2, window=10.0)
    assert flt.filter(_make_record()) is True
    assert flt.filter(_make_record()) is True
    assert flt.filter(_make_record()) is False


def test_sampling_filter_resets_after_window() -> None:
    flt = SamplingFilter(rate=1, window=0.05)
    assert flt.filter(_make_record()) is True
    assert flt.filter(_make_record()) is False  # exceeded within window
    time.sleep(0.06)
    assert flt.filter(_make_record()) is True  # window reset


def test_sampling_filter_always_passes_warning_and_above() -> None:
    flt = SamplingFilter(rate=1, window=10.0)
    # Exhaust the rate
    flt.filter(_make_record())
    flt.filter(_make_record())

    assert flt.filter(_make_record(logging.WARNING)) is True
    assert flt.filter(_make_record(logging.ERROR)) is True
    assert flt.filter(_make_record(logging.CRITICAL)) is True


def test_sampling_filter_invalid_rate_raises() -> None:
    with pytest.raises(ValueError, match="rate"):
        SamplingFilter(rate=0)


def test_sampling_filter_invalid_window_raises() -> None:
    with pytest.raises(ValueError, match="window"):
        SamplingFilter(rate=1, window=0.0)


# ---------------------------------------------------------------------------
# RedactionFilter tests
# ---------------------------------------------------------------------------


def test_redaction_filter_masks_default_sensitive_keys() -> None:
    flt = RedactionFilter()
    record = _make_record(msg="login")
    record.password = "s3cr3t"  # type: ignore[attr-defined]
    record.token = "tok123"  # type: ignore[attr-defined]

    result = flt.filter(record)

    assert result is True
    assert record.password == "***"  # type: ignore[attr-defined]
    assert record.token == "***"  # type: ignore[attr-defined]


def test_redaction_filter_leaves_non_sensitive_keys_unchanged() -> None:
    flt = RedactionFilter()
    record = _make_record(msg="safe")
    record.user_id = "u-1"  # type: ignore[attr-defined]
    record.request_id = "r-1"  # type: ignore[attr-defined]

    flt.filter(record)

    assert record.user_id == "u-1"  # type: ignore[attr-defined]
    assert record.request_id == "r-1"  # type: ignore[attr-defined]


def test_redaction_filter_custom_sensitive_keys() -> None:
    flt = RedactionFilter(sensitive_keys=["account_number", "ssn"])
    record = _make_record(msg="custom")
    record.account_number = "12345678"  # type: ignore[attr-defined]
    record.ssn = "999-99-9999"  # type: ignore[attr-defined]
    record.user_id = "u-1"  # type: ignore[attr-defined]

    flt.filter(record)

    assert record.account_number == "***"  # type: ignore[attr-defined]
    assert record.ssn == "***"  # type: ignore[attr-defined]
    assert record.user_id == "u-1"  # type: ignore[attr-defined]


def test_redaction_filter_does_not_touch_standard_fields() -> None:
    flt = RedactionFilter()
    record = _make_record(msg="standard")
    original_name = record.name
    original_levelname = record.levelname

    flt.filter(record)

    assert record.name == original_name
    assert record.levelname == original_levelname


def test_redaction_filter_key_matching_is_case_insensitive() -> None:
    flt = RedactionFilter()
    record = _make_record(msg="case")
    record.PASSWORD = "abc"  # type: ignore[attr-defined]
    record.Token = "xyz"  # type: ignore[attr-defined]

    flt.filter(record)

    assert record.PASSWORD == "***"  # type: ignore[attr-defined]
    assert record.Token == "***"  # type: ignore[attr-defined]
