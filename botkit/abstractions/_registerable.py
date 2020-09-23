from abc import ABC
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from botkit.routing.route_builder.builder import RouteBuilder
else:
    RouteBuilder = TypeVar("RouteBuilder")


class IRegisterable(ABC):
    @classmethod
    def register(cls, routes: RouteBuilder):
        pass
