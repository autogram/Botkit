from abc import abstractmethod
from logging import Logger
from typing import Any, Optional

from haps import base
from logzero import setup_logger

from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.route_builder.route_collection import RouteCollection
from botkit.settings import botkit_settings


@base
class Module:
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

    async def load(self) -> Optional[Any]:
        pass

    async def unload(self) -> None:
        pass

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @property
    def log(self) -> Logger:
        return self.logger

    @property
    def logger(self) -> Logger:
        if not getattr(self, "_logger", None):
            self._logger = setup_logger(
                self.__class__.__name__, formatter=botkit_settings.log_formatter
            )
        # noinspection Mypy
        return self._logger
