from abc import ABCMeta
from typing import Union, Optional, Callable, Awaitable

from botkit.routing.route_builder.route_collection import RouteCollection
from botkit.routing.triggers import RouteTriggers
from abc import ABC


class ActionExpressionBase(ABC):
    def __init__(
        self,
        routes: RouteCollection,
        action: Union[int, str],
        condition: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None,
    ):
        self._routes = routes
        self._triggers = RouteTriggers(
            action=action, filters=None, condition=condition
        )
