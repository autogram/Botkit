import re
from typing import Any, Dict, Union

from cached_property import cached_property
from haps import Container
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from botkit.persistence.callback_store import ICallbackStore
from botkit.routing.route import RouteHandler
from botkit.routing.triggers import ActionIdTypes
from botkit.routing.update_types.updatetype import UpdateType
from botkit.settings import botkit_settings
from botkit.types.client import IClient
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context

START_WITH_UUID4_ARG_REGEX = re.compile(r"^/start [0-9a-f-]{36}$", re.MULTILINE)

log = create_logger("deep_link_start_action_dispatcher")


class DeepLinkStartActionDispatcher:
    def __init__(self):
        self._action_routes: Dict[ActionIdTypes, RouteHandler] = dict()

    def add_action_route(self, route: RouteHandler):
        assert route.action_id is not None

        if route.action_id in self._action_routes:
            raise ValueError(f"Action ID {route.action_id} is not unique.")

        self._action_routes[route.action_id] = route

    @property
    def pyrogram_handler(self) -> MessageHandler:
        return MessageHandler(
            self.handle, filters=filters.text & filters.regex(START_WITH_UUID4_ARG_REGEX)
        )

    async def handle(self, client: IClient, message: Message) -> Union[bool, Any]:
        cb_ctx = self.callback_manager.lookup_callback(message.command[1:])  # asserted by regex
        if not cb_ctx:
            return False

        route = self._action_routes[cb_ctx.action]

        context: Context = Context(
            client=client,
            update=message,
            update_type=UpdateType.message,
            view_state=cb_ctx.state,
            action=cb_ctx.action,
            payload=cb_ctx.payload,
        )

        return await route.callback(client, message, context)

    @cached_property
    def callback_manager(self) -> ICallbackStore:
        return Container().get_object(ICallbackStore, botkit_settings.callback_manager_qualifier)
