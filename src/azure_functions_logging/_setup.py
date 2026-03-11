"""Logging setup and environment detection."""

from __future__ import annotations

import logging
import os

from ._context import ContextFilter
from ._formatter import ColorFormatter

# Track whether setup has been called to ensure idempotency
_setup_done: bool = False


def _is_functions_environment() -> bool:
    """Check if running inside Azure Functions (hosted or Core Tools)."""
    return bool(os.environ.get("FUNCTIONS_WORKER_RUNTIME"))


def _is_azure_hosted() -> bool:
    """Check if running in Azure-hosted environment (not local Core Tools)."""
    return bool(os.environ.get("WEBSITE_INSTANCE_ID"))


def setup_logging(
    *,
    level: int = logging.INFO,
    logger_name: str | None = None,
) -> None:
    """Configure logging for the current environment.

    Behavior depends on the detected environment:

    - **Azure / Core Tools**: Installs ``ContextFilter`` on the root logger's
      handlers only. Does NOT add handlers or modify the root logger level
      (respects ``host.json`` configuration).
    - **Standalone local development**: Adds a ``StreamHandler`` with
      ``ColorFormatter`` to the specified logger (or root logger if
      ``logger_name`` is None). Sets the level.

    This function is idempotent — calling it multiple times has no additional
    effect.

    Args:
        level: Logging level for local development. Ignored in Azure/Core Tools.
        logger_name: Optional logger name to configure. When None, configures
            the root logger (local dev) or installs filter on root handlers (Azure).
    """
    global _setup_done
    if _setup_done:
        return
    _setup_done = True

    context_filter = ContextFilter()

    if _is_functions_environment():
        # Azure or Core Tools: install filter only, don't touch handlers/level
        root = logging.getLogger()
        for handler in root.handlers:
            handler.addFilter(context_filter)
        # Also install on any future handlers via the logger itself
        root.addFilter(context_filter)
    else:
        # Standalone local development
        target = logging.getLogger(logger_name)
        target.setLevel(level)

        # Add colored handler only if no handlers exist
        if not target.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(ColorFormatter())
            handler.addFilter(context_filter)
            target.addHandler(handler)
        else:
            # Add filter to existing handlers
            for handler in target.handlers:
                handler.addFilter(context_filter)
