from __future__ import annotations

import asyncio
from functools import partial
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


def _to_thread_callable(
    func: Callable[..., T], /, *args: Any, **kwargs: Any
) -> Callable[[], T]:
    return partial(func, *args, **kwargs)


async def run_sync(func: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
    """Execute ``func`` in a thread pool and return its result.

    The helper centralises ``asyncio.to_thread`` usage so service layers can
    expose ``async`` APIs while reusing the existing synchronous SQLModel logic.
    """

    return await asyncio.to_thread(_to_thread_callable(func, *args, **kwargs))


async def ensure_awaitable(value: Any) -> Any:
    """Await ``value`` when it is awaitable, otherwise return it unchanged."""

    if asyncio.iscoroutine(value) or isinstance(value, Awaitable):
        return await value
    return value
