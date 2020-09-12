from typing import Dict, List, Optional

from pyrogram.filters import Filter

from botkit.routing.route import RouteDefinition
from botkit.types.client import IClient


class RouteCollection:
    def __init__(self, current_client: IClient = None):
        self.current_client = current_client
        self.routes_by_client: Dict[IClient, List[RouteDefinition]] = dict()
        self.default_filters: Optional[Filter] = None

    def add_for_current_client(self, route: RouteDefinition):
        if self.current_client is None:
            raise ValueError(
                "Please assign a client to the builder first by declaring `routes.use(client)` or using the "
                "contextmanager `with routes.using(client): ...`"
            )
        self._merge_route_trigger_with_default_filters(route)
        self.routes_by_client.setdefault(self.current_client, list()).append(route)

    def _merge_route_trigger_with_default_filters(self, route: RouteDefinition) -> None:

        if not self.default_filters:
            return

        if not (route_filters := route.triggers.filters):
            return

        route.triggers.filters = route_filters & self.default_filters
