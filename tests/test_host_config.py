from __future__ import annotations

import json
import logging
from pathlib import Path
import warnings

import pytest

from azure_functions_logging._host_config import warn_host_json_level_conflict


def _write_host_json(path: Path, content: dict[str, object]) -> None:
    path.write_text(json.dumps(content), encoding="utf-8")


def test_warns_when_host_level_is_more_restrictive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_host_json(
        tmp_path / "host.json",
        {"logging": {"logLevel": {"default": "Warning"}}},
    )
    monkeypatch.chdir(tmp_path)

    with pytest.warns(UserWarning, match="more restrictive") as warning_list:
        warn_host_json_level_conflict(logging.INFO)

    message = str(warning_list[0].message)
    assert "'Warning'" in message
    assert "'INFO'" in message


def test_no_warning_when_host_level_is_less_restrictive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_host_json(
        tmp_path / "host.json",
        {"logging": {"logLevel": {"default": "Information"}}},
    )
    monkeypatch.chdir(tmp_path)

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        warn_host_json_level_conflict(logging.WARNING)

    assert len(warning_list) == 0


def test_no_warning_when_host_json_does_not_exist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        warn_host_json_level_conflict(logging.INFO)

    assert len(warning_list) == 0


def test_no_warning_when_logging_config_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_host_json(tmp_path / "host.json", {"version": "2.0"})
    monkeypatch.chdir(tmp_path)

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        warn_host_json_level_conflict(logging.INFO)

    assert len(warning_list) == 0
