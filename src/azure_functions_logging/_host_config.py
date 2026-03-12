"""host.json logging configuration helpers."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import warnings

_HOST_LEVEL_TO_LOGGING: dict[str, int | None] = {
    "critical": logging.CRITICAL,
    "debug": logging.DEBUG,
    "error": logging.ERROR,
    "information": logging.INFO,
    "none": None,
    "trace": logging.DEBUG,
    "warning": logging.WARNING,
}


def warn_host_json_level_conflict(configured_level: int) -> None:
    """Warn when host.json suppresses logs below setup_logging level."""
    host_path = Path.cwd() / "host.json"
    if not host_path.exists():
        return

    try:
        host_config = json.loads(host_path.read_text(encoding="utf-8"))
    except Exception:
        return

    try:
        host_level = host_config["logging"]["logLevel"]["default"]
    except Exception:
        return

    if not isinstance(host_level, str):
        return

    resolved_level = _HOST_LEVEL_TO_LOGGING.get(host_level.lower())
    if resolved_level is None:
        return

    if resolved_level > configured_level:
        configured_level_name = logging.getLevelName(configured_level)
        warnings.warn(
            (
                f"host.json logLevel.default is set to '{host_level}' which is more restrictive "
                f"than the configured level '{configured_level_name}'. Logs below '{host_level}' "
                "will be suppressed by the Azure Functions host."
            ),
            stacklevel=3,
        )
