import asyncio
from typing import Any, Dict, Optional, Union

from cached_property import cached_property
from haps import Container
from loguru import logger as log
from pyrogram.filters import create
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import CallbackQuery

from botkit.core.components import Component
from botkit.core.modules import Module
from botkit.persistence.callback_store import CallbackActionContext, ICallbackStore
from botkit.routing.route import RouteHandler
from botkit.routing.triggers import ActionIdType
from tgtypes.updatetype import UpdateType
from botkit import botkit_settings
from botkit.clients.client import IClient
from botkit.botkit_context import Context
from botkit.widgets import Widget


class CallbackQueryActionDispatcher:
    def __init__(self, handle_errors: bool = True, alert_on_error: bool = True):
        self._action_routes: Dict[ActionIdType, RouteHandler] = dict()

        self.handle_errors = handle_errors
        self.alert_on_error = alert_on_error

        self.bot_restarted_error_message = (
            "Sorry, looks like the bot has been restarted in the meantime "
            "and doesn't know what you clicked on. Please start over!"
        )

        self.no_action_found_error_message = (
            "Sorry, but I am unsure how to handle this action at the moment."
        )

    def add_action_route(self, route: RouteHandler):
        assert route.action_id is not None

        if route.action_id in self._action_routes:
            raise ValueError(f"Action ID {route.action_id} is not unique.")

        self._action_routes[route.action_id] = route

    def localize_action_id(
        self, action_id: ActionIdType, module: Module, component: Component, widget: Widget
    ):
        """
        Make every action ID unique per module, component, or widget
        """
        raise NotImplementedError  # TODO

    @property
    def pyrogram_handler(self) -> CallbackQueryHandler:
        game_callback_filter = create(
            lambda _, __, cbq: bool(cbq.game_short_name), "GameCallbackQuery"
        )
        return CallbackQueryHandler(self.handle, filters=~game_callback_filter)

    async def handle(self, client: IClient, callback_query: CallbackQuery) -> Union[bool, Any]:
        cb_ctx: Optional[CallbackActionContext] = await self._get_context_or_respond(
            callback_query
        )
        if not cb_ctx:
            return False

        route = self._action_routes[cb_ctx.action]

        context: Context = Context(
            client=client,
            update=callback_query,
            update_type=UpdateType.callback_query,
            view_state=cb_ctx.state,
            action=cb_ctx.action,
            payload=cb_ctx.payload,
        )

        try:
            result = await route.callback(client, callback_query, context)
            if cb_ctx.notification:
                # Answer asynchronously, no need to wait.
                asyncio.ensure_future(
                    callback_query.answer(cb_ctx.notification, show_alert=cb_ctx.show_alert)
                )
            return result
        except:
            log.exception(f"A handler failed: {route.description}")
            await callback_query.answer(text="Sorry, something went wrong.", show_alert=False)
            return False

    @cached_property
    def callback_manager(self) -> ICallbackStore:
        return Container().get_object(ICallbackStore, botkit_settings.callback_store_qualifier)

    async def _get_context_or_respond(
        self, callback_query: CallbackQuery
    ) -> Optional[CallbackActionContext]:
        context = self.callback_manager.lookup_callback(callback_query.data)

        if not context:
            log.error("Could not find a callback query context.")
            if self.handle_errors:
                await callback_query.answer(
                    text=self.bot_restarted_error_message, show_alert=self.alert_on_error,
                )
            return None

        if context.action not in self._action_routes:
            if context.action.startswith("test_"):
                asyncio.ensure_future(
                    callback_query.answer("This button is just a UI mockup.", show_alert=False)
                )
                return None
            else:
                log.error("No route registered for callback query.")
                if self.handle_errors:
                    await callback_query.answer(
                        text=self.no_action_found_error_message, show_alert=self.alert_on_error,
                    )
                return None

        return context
