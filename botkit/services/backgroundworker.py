import asyncio
from abc import ABC, abstractmethod
from asyncio.exceptions import CancelledError
from asyncio.futures import Future
from typing import Any, NoReturn, Optional, Union

from loguru import logger as log

from botkit.abstractions import IAsyncLoadUnload


class BackgroundWorker(IAsyncLoadUnload, ABC):
    def __init__(self, initial_delay_seconds: Optional[int] = None):
        self.initial_delay_seconds = initial_delay_seconds
        self.worker_future: Optional[Future] = None
        self._has_been_running_before: bool = False

    def get_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    async def do_work(self):
        pass

    async def load(self) -> Union[NoReturn, Any]:
        if self.initial_delay_seconds and not self._has_been_running_before:
            await asyncio.sleep(self.initial_delay_seconds)

        self.worker_future = asyncio.ensure_future(self.do_work)
        self._has_been_running_before = True
        log.debug(f"Background worker {self.get_name()} started.")

    async def unload(self) -> NoReturn:
        try:
            self.worker_future.cancel("unload")
            log.debug(f"Background worker {self.get_name()} has shut down gracefully.")
        except CancelledError:
            log.debug(f"Background worker {self.get_name()} has been terminated.")
