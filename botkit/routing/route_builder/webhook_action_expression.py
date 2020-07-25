try:
    from httpx import AsyncClient
except:
    AsyncClient = None

from typing import Any
from typing_extensions import Literal

from botkit.routing.route_builder.action_expression_base import ActionExpressionBase

# client = AsyncClient()


# async def execute_request(url: str, method: Literal["POST", "GET"], state: Any, payload: Any):
#     await client.request(method, url, data=data)


class WebhookActionExpressionMixin(ActionExpressionBase):
    def post(self, url: str):
        return
        # plan = ExecutionPlan()
        # plan.add_handler()
        # route = Route(triggers=self._triggers, execution_plan=plan)
        # self._routes.add_for_current_client(route)
        # future = asyncio.ensure_future(self.execute_request(method="POST", choices=))

    def get(self, url: str):
        pass

    def _create_payload(self):
        pass


# async def build_handler()
