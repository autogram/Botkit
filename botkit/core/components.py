import logging
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Generic, Optional, TYPE_CHECKING, Type, TypeVar

from logzero import setup_logger

from botkit.routing.types import TViewState
from botkit.settings import botkit_settings
from botkit.views.botkit_context import Context

if TYPE_CHECKING:
    from botkit.routing.route_builder.builder import RouteBuilder
else:
    RouteBuilder = TypeVar("RouteBuilder")


# TODO: make sure components get properly destroyed/garbage collected when they're not needed anymore
# TODO: components can only have parameterless constructor..???

TCompState = TypeVar("TCompState")


class Component(Generic[TViewState, TCompState], ABC):
    _logger: Optional[Logger]
    _is_registered: str

    def __new__(cls, *args, **kwargs) -> Any:
        instance: Component = super().__new__(cls, *args, **kwargs)
        instance._is_registered = False
        return instance

    @abstractmethod
    def register(self, routes: RouteBuilder):
        ...

    @abstractmethod
    async def invoke(self, context: Context):
        ...

    @property
    def log(self) -> Logger:
        return self.logger

    @property
    def logger(self) -> Logger:
        if not getattr(self, "_logger", None):
            self._logger: Logger = setup_logger(
                self.__class__.__name__, formatter=botkit_settings.log_formatter
            )
            self._logger.setLevel(logging.INFO)
        # noinspection Mypy
        return self._logger
