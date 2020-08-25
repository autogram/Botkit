from typing import Any, List, Optional
from unittest.mock import Mock

from haps import Inject
from pyrogram import Chat, Message, User

from botkit.core.moduleloader import ModuleLoader
from botkit.core.modules import Module, module
from botkit.routing.pipelines.callbacks import HandlerSignature
from botkit.routing.route import RouteDefinition, RouteHandler
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.route_builder.route_collection import RouteCollection
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient


def notests(func):
    func.notests = True
    return func


class SystemTestsModule(Module):
    loader: ModuleLoader = Inject()

    def register(self, routes: RouteBuilder):
        pass

    async def load(self) -> None:
        for m in self.loader.modules:

            if not m.route_collection:
                continue

            for client, routes in m.route_collection.routes_by_client.items():
                await self.test_module_routes(routes)

    async def unload(self) -> None:
        return await super().unload()

    async def test_module_routes(self, routes: List[RouteDefinition]):
        for route in routes:
            for update_type, route_wrapper in route.handler_by_update_type.items():
                await self.fire_request(update_type, route_wrapper)

    async def fire_request(self, update_type: UpdateType, route: RouteHandler):
        try:
            should_not_test = route.callback.notests
            return
        except AttributeError:
            pass

        client = Mock(IClient)
        if update_type == UpdateType.message:
            message = Mock(Message)
            (user := Mock(User)).configure_mock()
            (chat := Mock(Chat)).configure_mock(id=12345)
            message.configure_mock(
                message_id=12345,
                command="test",
                from_user=user,
                chat=chat,
                text="test",
                forward_from=None,
                reply_to_message=None,
            )
            try:
                res = await route.callback(client, message)
                print(res)
            except Exception as ex:
                self.log.exception(ex)