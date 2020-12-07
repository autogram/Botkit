from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

import loguru

from botkit.abstractions import IAsyncLoadUnload, IRegisterable
from botkit.routing.types import TViewState
from botkit.botkit_context import Context

# TODO: make sure components get properly destroyed/garbage collected when they're not needed anymore
# TODO: components can only have parameterless constructor..???

TCompState = TypeVar("TCompState")


class Component(Generic[TViewState, TCompState], IAsyncLoadUnload, IRegisterable, ABC):
    _logger: Optional[loguru.Logger]
    _is_registered: bool

    _unique_index: Optional[int] = None
    _index_counter: int = 0

    def __new__(cls, *args, **kwargs) -> Any:
        Component._index_counter += 1
        instance: Component = super().__new__(cls, *args, **kwargs)
        instance._is_registered = False
        instance._unique_index = Component._index_counter
        return instance

    @abstractmethod
    async def invoke(self, context: Context):
        ...

    @property
    def log(self) -> loguru.Logger:
        return loguru.logger

    @property
    def logger(self) -> loguru.Logger:
        return loguru.logger
