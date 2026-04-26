"""Invocation context propagation via contextvars."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import contextvars
import logging
from typing import Any

# Context variables for invocation context
invocation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "invocation_id", default=None
)
function_name_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "function_name", default=None
)
trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)
cold_start_var: contextvars.ContextVar[bool | None] = contextvars.ContextVar(
    "cold_start", default=None
)

# Cold start detection
_cold_start: bool = True


def _check_cold_start() -> bool:
    """Check and consume the cold start flag. Returns True only on first call."""
    global _cold_start
    if _cold_start:
        _cold_start = False
        return True
    return False


class ContextFilter(logging.Filter):
    """Logging filter that copies contextvars values onto LogRecord attributes.

    This filter is installed on handlers (not loggers) so it covers ALL loggers
    including third-party libraries.
    """

    CONTEXT_FIELDS: tuple[str, ...] = (
        "invocation_id",
        "function_name",
        "trace_id",
        "cold_start",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context fields to the log record. Always returns True."""
        record.invocation_id = invocation_id_var.get()
        record.function_name = function_name_var.get()
        record.trace_id = trace_id_var.get()
        record.cold_start = cold_start_var.get()
        return True


def _extract_trace_id(trace_parent: str | None) -> str | None:
    """Extract trace_id from W3C traceparent header.

    Format: 00-<trace_id>-<parent_id>-<flags>
    """
    if not trace_parent:
        return None
    try:
        parts = trace_parent.split("-")
        if len(parts) >= 3:
            return parts[1]
    except Exception:  # nosec B110 — Principle 3: context failures are silent
        pass
    return None


def inject_context(context: Any) -> None:
    """Set invocation context from an Azure Functions context object.

    Extracts invocation_id, function_name, trace_id, and cold_start
    from the provided context and stores them in contextvars.

    This function is safe to call with any object. Missing or inaccessible
    attributes are silently ignored (Principle 3: context injection failures
    never cause application failures).

    Args:
        context: An Azure Functions context object (func.Context).
    """
    try:
        invocation_id_var.set(getattr(context, "invocation_id", None))
    except Exception:  # nosec B110 — Principle 3: context failures are silent
        invocation_id_var.set(None)

    try:
        function_name_var.set(getattr(context, "function_name", None))
    except Exception:  # nosec B110 — Principle 3: context failures are silent
        function_name_var.set(None)

    try:
        trace_context = getattr(context, "trace_context", None)
        trace_parent = getattr(trace_context, "trace_parent", None) if trace_context else None
        trace_id_var.set(_extract_trace_id(trace_parent))
    except Exception:  # nosec B110 — Principle 3: context failures are silent
        trace_id_var.set(None)

    try:
        cold_start_var.set(_check_cold_start())
    except Exception:  # nosec B110 — Principle 3: context failures are silent
        pass


def reset_context() -> None:
    """Clear every invocation context variable.

    Call this after an invocation completes when you used ``inject_context()``
    manually. Without resetting, contextvar values can leak across reused
    Azure Functions worker invocations and across async/thread boundaries —
    a subsequent log line may carry a stale ``invocation_id`` belonging to an
    earlier request.

    Safe to call repeatedly. Setting to ``None`` is the documented "absent"
    state for every context field (matches ``ContextVar`` defaults).
    """
    invocation_id_var.set(None)
    function_name_var.set(None)
    trace_id_var.set(None)
    cold_start_var.set(None)


@contextmanager
def logging_context(context: Any) -> Iterator[None]:
    """Context manager wrapping ``inject_context`` + ``reset_context``.

    Recommended pattern when handlers don't use the ``with_context`` decorator::

        def handler(req, context):
            with logging_context(context):
                logger.info("processing")
                ...

    Guarantees ``reset_context()`` runs even if the body raises, preventing
    invocation context from leaking into subsequent invocations on the same
    worker.
    """
    inject_context(context)
    try:
        yield
    finally:
        reset_context()
