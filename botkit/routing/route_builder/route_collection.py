from typing import Dict, List

from pyrogram import Client

from botkit.routing.route import RouteDefinition
from botkit.routing.update_types.updatetype import UpdateType


class RouteCollection:
    def __init__(self, current_client: Client = None):
        self.current_client = current_client
        self.routes_by_client: Dict[Client, List[RouteDefinition]] = dict()

    def add_for_current_client(self, route: RouteDefinition):
        if self.current_client is None:
            raise ValueError(
                "Please assign a client to the builder first by declaring `routes.use(client)` or using the "
                "contextmanager `with routes.using(client): ...`"
            )
        self.routes_by_client.setdefault(self.current_client, list()).append(route)

    # @property
    # def client_routes_by_update_type(self) -> Dict[Client, Dict[UpdateType, List[Route]]]:
    #     result = {}
    #     for c, r_list in self.routes.items():
    #         result.setdefault(c, {})
    #
    #         for route in r_list:
    #             result[c].setdefault(route.plan.update_types, []).append(route)
    #
    #     return result
