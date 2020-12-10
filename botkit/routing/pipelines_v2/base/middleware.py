from abc import ABC, abstractmethod
from typing import Any, Coroutine, Set

from botkit.botkit_context import Context
from botkit.routing.pipelines_v2.base._abstractions import (
    NextDelegate,
    TContext,
    AbstractGenericMiddleware,
)
from tgtypes.updatetype import UpdateType


class BaseMiddleware(AbstractGenericMiddleware[Context], ABC):
    @abstractmethod
    async def __call__(self, context: Context, call_next: NextDelegate[Context]) -> Any:
        ...


EventType = UpdateType  # for now..


class ConditionalMiddleware(BaseMiddleware, ABC):
    @property
    @abstractmethod
    def applicable_event_types(self) -> Set[EventType]:
        ...
