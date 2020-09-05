from typing import Type

from botkit.core.modules import Module
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.route_builder.route_collection import RouteCollection


def register_module_with_route_builder(
    module: Module, route_builder_type: Type[RouteBuilder]
) -> RouteCollection:
    builder = route_builder_type()
    module.register(builder)
    module.route_collection = builder._route_collection
    return builder._route_collection
