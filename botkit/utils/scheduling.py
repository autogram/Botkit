import asyncio
from typing import Optional


def maybe_async(func, *args, **kwargs):
    """
    Turn a callable into a coroutine if it isn't
    """

    if asyncio.iscoroutine(func):
        return func

    return asyncio.coroutine(func)(*args, **kwargs)


def fire(func, *args, **kwargs):
    """
    Fire a callable as a coroutine, and return its future. The cool thing
    about this function is that (via maybeAsync) it lets you treat synchronous
    and asynchronous callables the same, which simplifies code.
    """

    return asyncio.ensure_future(maybe_async(func, *args, **kwargs))


async def _call_later(delay, func, *args, **kwargs):
    """
    The bus stop, where we wait.
    """

    await asyncio.sleep(delay)
    fire(func, *args, **kwargs)


def call_later(delay, func, *args, **kwargs):
    """
    After :delay seconds, call :callable with :args and :kwargs; :callable can
    be a synchronous or asynchronous callable (a coroutine). Note that _this_
    function is synchronous - mission accomplished - it can be used from within
    any synchronous or asynchronous callable.
    """

    fire(_call_later, delay, func, *args, **kwargs)


def run_ignore_exc(coro, timeout: Optional[float] = None) -> asyncio.Future:
    async def inner():
        try:
            if timeout is not None:
                await asyncio.sleep(timeout)
            await coro
        except:
            pass

    return asyncio.ensure_future(inner())
