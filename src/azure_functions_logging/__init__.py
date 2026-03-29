"""azure-functions-logging — Developer-friendly logging for Azure Functions Python."""

from __future__ import annotations

from ._context import inject_context
from ._decorator import with_context
from ._filters import RedactionFilter, SamplingFilter
from ._json_formatter import JsonFormatter
from ._logger import FunctionLogger
from ._setup import setup_logging

__all__ = [
    "__version__",
    "FunctionLogger",
    "JsonFormatter",
    "RedactionFilter",
    "SamplingFilter",
    "get_logger",
    "inject_context",
    "setup_logging",
    "with_context",
]

__version__ = "0.4.1"


def get_logger(name: str | None = None) -> FunctionLogger:
    """Create a ``FunctionLogger`` wrapping a standard ``logging.Logger``.

    Args:
        name: Logger name. Typically ``__name__``.

    Returns:
        A ``FunctionLogger`` instance.
    """
    import logging

    return FunctionLogger(logging.getLogger(name))
