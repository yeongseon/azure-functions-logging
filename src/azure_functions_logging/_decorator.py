"""Decorator helper for automatic context injection.

Provides ``with_context`` — a decorator that calls ``inject_context()``
before the handler runs and resets context variables after it completes.

Ref: https://github.com/yeongseon/azure-functions-logging-python/issues/22
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable, TypeVar, overload

from ._context import (
    cold_start_var,
    function_name_var,
    inject_context,
    invocation_id_var,
    trace_id_var,
)

_F = TypeVar("_F", bound=Callable[..., Any])

_DEFAULT_PARAM = "context"


def _reset_context_vars() -> None:
    """Reset all invocation context variables to None."""
    invocation_id_var.set(None)
    function_name_var.set(None)
    trace_id_var.set(None)
    cold_start_var.set(None)


def _find_context_arg(
    func: Callable[..., Any],
    param: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Locate the context argument by parameter name."""
    # Check kwargs first
    if param in kwargs:
        return kwargs[param]

    # Fall back to positional args
    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        idx = params.index(param)
        if idx < len(args):
            return args[idx]
    except (ValueError, IndexError):
        pass

    return None


def _wrap_sync(func: _F, param: str) -> _F:
    """Wrap a synchronous handler."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = _find_context_arg(func, param, args, kwargs)
        if ctx is not None:
            inject_context(ctx)
        try:
            return func(*args, **kwargs)
        finally:
            _reset_context_vars()

    return wrapper  # type: ignore[return-value]


def _wrap_async(func: _F, param: str) -> _F:
    """Wrap an asynchronous handler."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = _find_context_arg(func, param, args, kwargs)
        if ctx is not None:
            inject_context(ctx)
        try:
            return await func(*args, **kwargs)
        finally:
            _reset_context_vars()

    return wrapper  # type: ignore[return-value]


@overload
def with_context(func: _F) -> _F: ...


@overload
def with_context(*, param: str = ...) -> Callable[[_F], _F]: ...


def with_context(
    func: _F | None = None,
    *,
    param: str = _DEFAULT_PARAM,
) -> _F | Callable[[_F], _F]:
    """Decorator that automatically injects invocation context.

    Can be used with or without arguments::

        @with_context
        def handler(req, context):
            ...

        @with_context(param="ctx")
        def handler(req, ctx):
            ...

    The decorator:

    1. Finds the ``context`` parameter (by name, default ``"context"``)
    2. Calls ``inject_context(context)`` before the handler body
    3. Resets all context variables in ``finally`` after the handler returns

    Both sync and async handlers are supported.

    Args:
        func: The handler function (when used without parentheses).
        param: Name of the parameter that receives the Azure Functions
            context object. Defaults to ``"context"``.
    """

    def decorator(fn: _F) -> _F:
        if asyncio.iscoroutinefunction(fn):
            return _wrap_async(fn, param)
        return _wrap_sync(fn, param)

    if func is not None:
        # Called as @with_context (no parentheses)
        return decorator(func)

    # Called as @with_context(...) (with parentheses)
    return decorator
