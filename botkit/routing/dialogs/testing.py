import asyncio

from botkit.routing.dialogs.history import CoroutineHistoryWrapper
from botkit.routing.dialogs.state import _call_and_jump


async def func(value):
    a = 15
    print(1)
    b = 27
    await asyncio.sleep(1)
    print(a, b)
    print(2)
    print(3)
    return value


async def wrap(coro):
    return await CoroutineHistoryWrapper(*await coro)


print(asyncio.run(wrap(_call_and_jump(func, 2, dict(a=15), kwargs={"value": 5}))))
