from typing import Protocol, TYPE_CHECKING

from botkit.agnostic import HandlerSignature
from botkit.routing.route_builder.has_route_collection import IRouteCollection
from botkit.routing.triggers import RouteTriggers

if TYPE_CHECKING:
    from botkit.routing.route_builder.expressions import RouteExpression
    from botkit.routing.route_builder.route_collection import RouteCollection


class IExpressionWithCallMethod(IRouteCollection, Protocol):
    _triggers: RouteTriggers

    def call(self, handler: HandlerSignature) -> "RouteExpression":
        pass
