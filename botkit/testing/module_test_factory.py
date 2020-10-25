from typing import Any, List, Type

from botkit.core.modules import Module
from botkit.routing.route import RouteDefinition
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.agnostic import PyrogramViewSender

# TODO: implement


class ModuleTestFactory:
    def __init__(self, module_type: Type):
        self.module_under_test = module_type

    def handle_update(self, update: Any, with_client: PyrogramViewSender):
        routes = self.get_routes()

    def get_routes(self, client: PyrogramViewSender) -> List[RouteDefinition]:
        module = self._create_instance()
        builder = RouteBuilder()
        module.register(builder)
        return builder._route_collection.routes_by_client[client]

    def _create_instance(self) -> Module:
        return self.module_under_test()
