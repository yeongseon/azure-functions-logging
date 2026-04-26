"""host.json logging configuration helpers."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import warnings

_HOST_LEVEL_TO_LOGGING: dict[str, int] = {
    "critical": logging.CRITICAL,
    "debug": logging.DEBUG,
    "error": logging.ERROR,
    "information": logging.INFO,
    "none": logging.CRITICAL + 10,
    "trace": logging.DEBUG,
    "warning": logging.WARNING,
}


def _resolve_host_level(value: object) -> int | None:
    if not isinstance(value, str):
        return None
    return _HOST_LEVEL_TO_LOGGING.get(value.lower())


def warn_host_json_level_conflict(configured_level: int) -> None:
    """Warn when any ``host.json`` ``logLevel`` entry suppresses logs below ``configured_level``.

    Azure Functions honors category-specific keys under ``logging.logLevel``
    (e.g. ``Function``, ``Function.<name>``, ``Host.Results``,
    ``Host.Aggregator``) in addition to ``default``. Inspecting only ``default``
    misses the common case where ``default = Information`` while a specific
    function category is set to ``Warning`` or ``None`` and silently drops the
    user's logs.

    This helper iterates every category and warns once per offending entry.
    """
    host_path = Path.cwd() / "host.json"
    if not host_path.exists():
        return

    try:
        host_config = json.loads(host_path.read_text(encoding="utf-8"))
    except Exception:
        return

    try:
        log_levels = host_config["logging"]["logLevel"]
    except Exception:
        return

    if not isinstance(log_levels, dict):
        return

    configured_level_name = logging.getLevelName(configured_level)

    for category, raw_level in log_levels.items():
        if not isinstance(category, str):
            continue
        resolved_level = _resolve_host_level(raw_level)
        if resolved_level is None:
            continue
        if resolved_level <= configured_level:
            continue

        scope = "default" if category == "default" else f"category '{category}'"
        warnings.warn(
            (
                f"host.json logLevel for {scope} is set to '{raw_level}' which is more "
                f"restrictive than the configured level '{configured_level_name}'. Logs "
                f"below '{raw_level}' will be suppressed by the Azure Functions host."
            ),
            stacklevel=3,
        )
