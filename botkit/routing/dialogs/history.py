import asyncio
import inspect
from dataclasses import dataclass

import sys
import threading
from typing import Any, Coroutine, List, Hashable, Tuple


class CoroutineHistoryWrapper:
    __slots__ = ("coro", "history")

    def __init__(self, coro, history: List[HistoryItem]):
        self.coro: Coroutine = coro
        self.history = history

    def __await__(self):
        i = 0
        next_ret = None
        try:
            while True:
                try:
                    request = self.coro.send(next_ret)
                except StopIteration as e:
                    return e.value
                except Exception as e:
                    yield self.coro.throw(*sys.exc_info())
                else:
                    if i < len(self.history):
                        history_item = self.history[i]
                        assert history_item[0] == request
                        next_ret = history_item[1]
                    else:
                        next_ret = yield request
                        self._add_history(request, next_ret)
        finally:
            yield self.coro.close()

    def _add_history(self, request, result):
        self.history.append((_hash_coroutine(request), result))


def _hash_coroutine(coroutine):
    return _hash_code(coroutine.cr_code)


def _hash_function(function):
    return _hash_code(function.co_code)


def _hash_code(code):
    return hash(code.replace(co_name=""))


@dataclass
class _DevVersion:
    hash: int


@dataclass
class HistoryItem:
    hash: Any


async def test():
    async def func(value):
        a = 15
        print(1)
        b = 27
        await asyncio.sleep(1)
        print(a, b)
        print(2)
        print(3)

        return value

    await CoroutineHistoryWrapper(func(3), History(None, []))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test())
