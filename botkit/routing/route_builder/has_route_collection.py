from typing import Protocol

from botkit.routing.route_builder.route_collection import RouteCollection


class IRouteCollection(Protocol):
    _route_collection: "RouteCollection"
