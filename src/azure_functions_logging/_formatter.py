"""Log formatters for azure-functions-logging."""

from __future__ import annotations

import logging
import sys

# ANSI color codes
_COLORS: dict[int, str] = {
    logging.DEBUG: "\033[90m",  # Gray
    logging.INFO: "\033[34m",  # Blue
    logging.WARNING: "\033[33m",  # Yellow
    logging.ERROR: "\033[31m",  # Red
    logging.CRITICAL: "\033[1;31m",  # Bold Red
}
_RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    """Colorized log formatter for local development.

    Format: ``HH:MM:SS LEVEL  logger_name  message [context_fields]``

    Context fields (invocation_id, function_name, etc.) are appended
    when present on the LogRecord (set by ContextFilter).
    """

    def __init__(self) -> None:
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with colors and context fields."""
        # Time
        time_str = self.formatTime(record, "%H:%M:%S")

        # Level with color
        color = _COLORS.get(record.levelno, "")
        level_str = f"{color}{record.levelname:<8}{_RESET}"

        # Logger name
        name_str = record.name

        # Message
        msg = record.getMessage()

        # Context fields
        context_parts: list[str] = []
        for field in ("invocation_id", "function_name", "trace_id"):
            value = getattr(record, field, None)
            if value is not None:
                context_parts.append(f"{field}={value}")

        cold_start = getattr(record, "cold_start", None)
        if cold_start is True:
            context_parts.append("cold_start=true")

        # Build output
        base = f"{time_str} {level_str} {name_str}  {msg}"
        if context_parts:
            base += f"  [{', '.join(context_parts)}]"

        # Exception info
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            base += f"\n{record.exc_text}"
        if record.stack_info:
            base += f"\n{record.stack_info}"

        return base

    @staticmethod
    def is_tty() -> bool:
        """Check if stderr supports color output."""
        return hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
