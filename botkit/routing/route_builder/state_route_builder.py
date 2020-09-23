from uuid import UUID, uuid4

from botkit.routing.route_builder.route_builder_base import RouteBuilderBase
from botkit.routing.route_builder.route_collection import RouteCollection


class StateRouteBuilder(RouteBuilderBase):
    def __init__(self, machine_guid: UUID, index: int, routes: RouteCollection, name: str = None):
        super().__init__(routes)
        self.state_guid = uuid4()
        self.machine_guid = machine_guid
        self.index = index
        self.name = name
        self._route_collection = routes
