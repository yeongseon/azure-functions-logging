"""FunctionLogger wrapper for azure-functions-logging."""

from __future__ import annotations

import logging
from typing import Any


class FunctionLogger:
    """Wrapper around a standard ``logging.Logger`` with context binding.

    ``FunctionLogger`` delegates all standard logging methods to the underlying
    logger. The ``bind()`` method returns a new wrapper with additional context
    fields that are merged into ``extra`` on each log call.

    Context from ``bind()`` is supplementary to the ``ContextFilter``-based
    context (invocation_id, function_name, etc.) which is set globally via
    ``inject_context()``.
    """

    __slots__ = ("_logger", "_context")

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._context: dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Return the name of the underlying logger."""
        return self._logger.name

    def bind(self, **kwargs: Any) -> FunctionLogger:
        """Return a new ``FunctionLogger`` with additional bound context.

        The returned logger shares the same underlying ``logging.Logger``
        but carries merged context fields. This is an immutable operation.

        Args:
            **kwargs: Context key-value pairs to bind.

        Returns:
            A new ``FunctionLogger`` with merged context.
        """
        new = FunctionLogger(self._logger)
        new._context = {**self._context, **kwargs}
        return new

    def clear_context(self) -> None:
        """Clear all bound context fields."""
        self._context = {}

    def _log(
        self,
        level: int,
        msg: object,
        args: tuple[Any, ...],
        exc_info: Any = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        **kwargs: Any,
    ) -> None:
        """Internal log dispatch with context injection."""
        if not self._logger.isEnabledFor(level):
            return
        extra = kwargs.pop("extra", None) or {}
        extra.update(self._context)
        self._logger.log(
            level,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            **kwargs,
        )

    def debug(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Log a DEBUG message."""
        self._log(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Log an INFO message."""
        self._log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Log a WARNING message."""
        self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR message."""
        self._log(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Log a CRITICAL message."""
        self._log(logging.CRITICAL, msg, args, **kwargs)

    def exception(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR message with exception info."""
        kwargs["exc_info"] = kwargs.get("exc_info", True)
        self._log(logging.ERROR, msg, args, **kwargs)

    def setLevel(self, level: int | str) -> None:
        """Set the logging level of the underlying logger."""
        self._logger.setLevel(level)

    def isEnabledFor(self, level: int) -> bool:
        """Check if the underlying logger is enabled for the given level."""
        return self._logger.isEnabledFor(level)

    def getEffectiveLevel(self) -> int:
        """Return the effective level of the underlying logger."""
        return self._logger.getEffectiveLevel()
