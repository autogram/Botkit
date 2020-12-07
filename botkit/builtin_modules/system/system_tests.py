from typing import List
from unittest.mock import Mock

from haps import Container, Inject
from pyrogram.types import Chat, Message, User

from botkit.core.modules import Module
from botkit.core.modules.activation import ModuleLoader
from botkit.persistence.callback_store import ICallbackStore
from botkit.routing.route import RouteDefinition, RouteHandler
from botkit.routing.route_builder.builder import RouteBuilder
from tgtypes.updatetype import UpdateType
from botkit import botkit_settings
from botkit.clients.client import IClient
from injector import inject


def notests(func):
    func.notests = True
    return func


class SelftestModule(Module):
    loader: ModuleLoader = Inject()

    @inject
    def __init__(self, callback_store: ICallbackStore) -> None:
        self.callback_store = callback_store

    def register(self, routes: RouteBuilder):
        pass

    async def load(self) -> None:
        return  # TODO: implement
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
            # noinspection PyUnresolvedReferences
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
