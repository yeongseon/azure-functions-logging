from __future__ import annotations

import logging
from unittest.mock import MagicMock

from azure_functions_logging._logger import FunctionLogger


def _mock_underlying_logger() -> MagicMock:
    logger = MagicMock(spec=logging.Logger)
    logger.name = "mock.logger"
    logger.isEnabledFor.return_value = True
    logger.getEffectiveLevel.return_value = logging.INFO
    return logger


def test_function_logger_delegates_to_underlying_logger() -> None:
    underlying = _mock_underlying_logger()
    logger = FunctionLogger(underlying)

    logger.info("hello")

    underlying.log.assert_called_once()
    args, kwargs = underlying.log.call_args
    assert args[0] == logging.INFO
    assert args[1] == "hello"
    assert kwargs["extra"] == {}


def test_bind_returns_new_instance_with_merged_context() -> None:
    logger = FunctionLogger(_mock_underlying_logger())
    bound = logger.bind(a=1, b=2)

    assert bound is not logger
    assert bound._context == {"a": 1, "b": 2}


def test_bind_does_not_mutate_original() -> None:
    logger = FunctionLogger(_mock_underlying_logger())
    _ = logger.bind(a=1)

    assert logger._context == {}


def test_bind_chaining_merges_context() -> None:
    logger = FunctionLogger(_mock_underlying_logger())
    chained = logger.bind(a=1).bind(b=2)

    assert chained._context == {"a": 1, "b": 2}


def test_clear_context() -> None:
    logger = FunctionLogger(_mock_underlying_logger()).bind(a=1)

    logger.clear_context()

    assert logger._context == {}


def test_all_log_methods() -> None:
    underlying = _mock_underlying_logger()
    logger = FunctionLogger(underlying)

    logger.debug("d")
    logger.info("i")
    logger.warning("w")
    logger.error("e")
    logger.critical("c")
    logger.exception("x")

    assert underlying.log.call_count == 6
    levels = [call.args[0] for call in underlying.log.call_args_list]
    assert levels == [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
        logging.ERROR,
    ]
    assert underlying.log.call_args_list[-1].kwargs["exc_info"] is True


def test_extra_from_bind_passed_to_underlying_logger() -> None:
    underlying = _mock_underlying_logger()
    logger = FunctionLogger(underlying).bind(user_id="u1")

    logger.info("msg", extra={"request_id": "r1"})

    _, kwargs = underlying.log.call_args
    assert kwargs["extra"] == {"request_id": "r1", "user_id": "u1"}


def test_arbitrary_kwargs_are_merged_into_extra() -> None:
    underlying = _mock_underlying_logger()
    logger = FunctionLogger(underlying).bind(function_id="f1")

    logger.info("order accepted", order_id="o-999", tenant_id="t-1")

    _, kwargs = underlying.log.call_args
    assert kwargs["extra"] == {
        "order_id": "o-999",
        "tenant_id": "t-1",
        "function_id": "f1",
    }


def test_is_enabled_for_get_effective_level_and_set_level() -> None:
    underlying = _mock_underlying_logger()
    logger = FunctionLogger(underlying)

    logger.setLevel(logging.DEBUG)
    underlying.setLevel.assert_called_once_with(logging.DEBUG)

    assert logger.isEnabledFor(logging.INFO) is True
    underlying.isEnabledFor.assert_called_with(logging.INFO)

    assert logger.getEffectiveLevel() == logging.INFO
    underlying.getEffectiveLevel.assert_called_once_with()


def test_name_property() -> None:
    logger = FunctionLogger(_mock_underlying_logger())
    assert logger.name == "mock.logger"


def test_log_returns_early_when_level_disabled() -> None:
    underlying = _mock_underlying_logger()
    underlying.isEnabledFor.return_value = False
    logger = FunctionLogger(underlying)

    logger.info("should not log", order_id="o-999")

    underlying.log.assert_not_called()
