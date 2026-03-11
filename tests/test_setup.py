from __future__ import annotations

import logging
import os
from unittest.mock import patch

import pytest

import azure_functions_logging._setup as setup_mod
from azure_functions_logging._context import ContextFilter
from azure_functions_logging._formatter import ColorFormatter
from azure_functions_logging._setup import (
    _is_azure_hosted,
    _is_functions_environment,
    setup_logging,
)


@pytest.fixture(autouse=True)
def reset_setup_state() -> None:
    setup_mod._setup_done = False


def test_setup_logging_local_dev_adds_handler_with_color_formatter() -> None:
    logger_name = "afl.test.local"
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.filters.clear()

    with patch.dict(os.environ, {}, clear=True):
        setup_logging(logger_name=logger_name, level=logging.DEBUG)

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0].formatter, ColorFormatter)

    logger.handlers.clear()
    logger.filters.clear()


def test_setup_logging_azure_env_adds_only_filter() -> None:
    root = logging.getLogger()
    root.filters.clear()
    test_handler = logging.StreamHandler()
    root.handlers = [test_handler]

    with patch.dict(os.environ, {"FUNCTIONS_WORKER_RUNTIME": "python"}, clear=True):
        setup_logging()

    assert root.handlers == [test_handler]
    assert any(isinstance(flt, ContextFilter) for flt in root.filters)
    assert any(isinstance(flt, ContextFilter) for flt in test_handler.filters)

    root.handlers = []
    root.filters.clear()


def test_setup_logging_is_idempotent() -> None:
    logger_name = "afl.test.idempotent"
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.filters.clear()

    with patch.dict(os.environ, {}, clear=True):
        setup_logging(logger_name=logger_name)
        first_handlers = list(logger.handlers)
        setup_logging(logger_name=logger_name)

    assert logger.handlers == first_handlers

    logger.handlers.clear()
    logger.filters.clear()


def test_is_functions_environment() -> None:
    with patch.dict(os.environ, {}, clear=True):
        assert _is_functions_environment() is False
    with patch.dict(os.environ, {"FUNCTIONS_WORKER_RUNTIME": "python"}, clear=True):
        assert _is_functions_environment() is True


def test_is_azure_hosted() -> None:
    with patch.dict(os.environ, {}, clear=True):
        assert _is_azure_hosted() is False
    with patch.dict(os.environ, {"WEBSITE_INSTANCE_ID": "abc123"}, clear=True):
        assert _is_azure_hosted() is True
