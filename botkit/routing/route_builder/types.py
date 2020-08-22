from typing import Protocol, TYPE_CHECKING, Type, TypeVar, Union

from botkit.routing.triggers import RouteTriggers
from botkit.views.base import InlineResultViewBase
from botkit.views.views import MessageViewBase

if TYPE_CHECKING:
    from botkit.routing.route_builder.builder import RouteExpression
else:
    RouteExpression = None

from botkit.routing.pipelines.callbacks import HandlerSignature

if TYPE_CHECKING:
    from botkit.routing.route_builder.route_collection import RouteCollection
else:
    RouteCollection = None


class IExpressionWithCallMethod(Protocol):
    _triggers: RouteTriggers
    _route_collection: "RouteCollection"

    def call(self, handler: HandlerSignature) -> RouteExpression:
        pass


V = TypeVar("V", bound=InlineResultViewBase, covariant=True)

TView = Union[V, Type[MessageViewBase]]
