from typing import Any, List, Type

from botkit.core.modules import Module
from botkit.routing.route import RouteDefinition
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.views.renderer_client_mixin import PyroRendererClientMixin

# TODO: implement


class ModuleTestFactory:
    def __init__(self, module_type: Type):
        self.module_under_test = module_type

    def handle_update(self, update: Any, with_client: PyroRendererClientMixin):
        routes = self.get_routes()

    def get_routes(self, client: PyroRendererClientMixin) -> List[RouteDefinition]:
        module = self._create_instance()
        builder = RouteBuilder()
        module.register(builder)
        return builder._route_collection.routes_by_client[client]

    def _create_instance(self) -> Module:
        return self.module_under_test()
