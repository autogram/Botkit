import logging
from logging import Logger
from typing import Generic, TYPE_CHECKING, TypeVar, Optional

from abc import abstractmethod, ABCMeta, ABC

from logzero import setup_logger

from botkit.builders.quizbuilder import QuizBuilder
from botkit.routing.types import TState
from botkit.views.botkit_context import BotkitContext
from botkit.views.views import PollBuilder

if TYPE_CHECKING:
    from botkit.routing.route_builder.builder import RouteBuilder
else:
    RouteBuilder = TypeVar("RouteBuilder")

from botkit.views.functional_views import view


# TODO: make sure components get properly destroyed/garbage collected when they're not needed anymore
# TODO: components can only have parameterless constructor..???


class Component(Generic[TState], ABC):
    _logger: Optional[Logger]

    @abstractmethod
    def register(self, routes: RouteBuilder):
        ...

    @abstractmethod
    async def invoke(self, context: BotkitContext):
        ...

    @property
    def log(self) -> Logger:
        return self.logger

    @property
    def logger(self) -> Logger:
        if not getattr(self, "_logger", None):
            self._logger: Logger = setup_logger(self.__class__.__name__)
            self._logger.setLevel(logging.INFO)
        # noinspection Mypy
        return self._logger
