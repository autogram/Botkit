from __future__ import annotations

from abc import abstractmethod
from typing import Any, Optional

import loguru
from haps import base
from loguru._logger import Logger

from botkit.abstractions import IAsyncLoadUnload
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.route_builder.route_collection import RouteCollection


@base
class Module(IAsyncLoadUnload):  # Not marked as ABC to allow dynamic creation
    _logger: Optional[Logger]

    # Properties assigned by the ModuleLoader
    route_collection: Optional[RouteCollection] = None
    index: Optional[int] = None

    _index_counter: int = 0

    def __new__(cls, *args, **kwargs) -> Any:
        Module._index_counter += 1
        instance = super().__new__(cls)
        instance.index = Module._index_counter
        return instance

    @abstractmethod
    def register(self, routes: RouteBuilder):
        pass

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @property
    def log(self) -> loguru.Logger:
        return loguru.logger

    @property
    def logger(self) -> loguru.Logger:
        return loguru.logger
