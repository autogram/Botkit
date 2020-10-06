from typing import *

T = TypeVar("T")


class AsyncLazyDict(Dict):
    async def setdefault_lazy(self, key, coro: Coroutine[Any, Any, T]) -> T:
        if self.get(key):
            return key
        self[key] = (val := await coro)
        return val
