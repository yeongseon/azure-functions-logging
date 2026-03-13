"""JSON log formatter for azure-functions-logging."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging

_STANDARD_RECORD_FIELDS: set[str] = {
    "args",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}
_CONTEXT_FIELDS: set[str] = {
    "invocation_id",
    "function_name",
    "trace_id",
    "cold_start",
}


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter.

    Output is newline-delimited JSON (NDJSON), with one JSON object per log line.
    Context fields (invocation_id, function_name, etc.) are included when present
    on the LogRecord (set by ContextFilter).
    """

    def __init__(self) -> None:
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as one NDJSON object."""
        message = record.getMessage()
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()

        exception: str | None = None
        if record.exc_info:
            exception = self.formatException(record.exc_info)

        excluded_fields = _STANDARD_RECORD_FIELDS | _CONTEXT_FIELDS
        extra = {key: value for key, value in record.__dict__.items() if key not in excluded_fields}

        payload = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "invocation_id": getattr(record, "invocation_id", None),
            "function_name": getattr(record, "function_name", None),
            "trace_id": getattr(record, "trace_id", None),
            "cold_start": getattr(record, "cold_start", None),
            "exception": exception,
            "extra": extra,
        }

        return f"{json.dumps(payload, ensure_ascii=False)}\n"
