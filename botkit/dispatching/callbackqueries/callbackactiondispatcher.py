import asyncio
from typing import Any, Dict, Optional, Union

from cached_property import cached_property
from haps import Container
from logzero import logger as log
from pyrogram.filters import create
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import CallbackQuery, Update

from botkit.persistence.callback_manager import CallbackActionContext, ICallbackManager
from botkit.routing.route import RouteDefinition, RouteHandler
from botkit.routing.triggers import ActionIdTypes
from botkit.settings import botkit_settings
from botkit.types.client import IClient
from botkit.views.botkit_context import Context


class CallbackActionDispatcher:
    def __init__(self, handle_errors: bool = True, alert_on_error: bool = True):
        self._action_routes: Dict[ActionIdTypes, RouteHandler] = dict()

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
        self._action_routes[route.action_id] = route

    @property
    def pyrogram_handler(self) -> CallbackQueryHandler:
        game_callback_filter = create(
            lambda _, __, cbq: bool(cbq.game_short_name), "GameCallbackQuery"
        )
        return CallbackQueryHandler(self.handle, filters=~game_callback_filter)

    @staticmethod
    def check(client: IClient, update: Update, route: RouteDefinition):
        return (
            route.triggers.filters(client, update)
            if callable(route.triggers.filters)
            else True
        )

    async def handle(
        self, client: IClient, callback_query: CallbackQuery
    ) -> Union[bool, Any]:
        cb_ctx: Optional[CallbackActionContext] = await self._get_context_or_respond(
            callback_query
        )
        if not cb_ctx:
            return False

        route = self._action_routes[cb_ctx.action]
        print(route)

        context: Context = Context(
            client=client,
            update=callback_query,
            state=cb_ctx.state,
            action=cb_ctx.action,
            payload=cb_ctx.payload,
        )

        try:
            result = await route.callback(client, callback_query, context)
            if cb_ctx.notification:
                # Answer asynchronously, no need to wait.
                asyncio.ensure_future(
                    callback_query.answer(
                        cb_ctx.notification, show_alert=cb_ctx.show_alert
                    )
                )
            return result
        except:
            log.exception(f"A handler failed: {route.description}")
            await callback_query.answer(
                text="Sorry, something went wrong.", show_alert=False
            )
            return False

    @cached_property
    def callback_manager(self) -> ICallbackManager:
        return Container().get_object(
            ICallbackManager, botkit_settings.callback_manager_qualifier
        )

    async def _get_context_or_respond(
        self, callback_query: CallbackQuery
    ) -> Optional[CallbackActionContext]:
        context = self.callback_manager.lookup_callback(callback_query.data)

        if not context:
            log.error("Could not find a callback query context.")
            if self.handle_errors:
                await callback_query.answer(
                    text=self.bot_restarted_error_message,
                    show_alert=self.alert_on_error,
                )
            return None

        if context.action not in self._action_routes:
            log.error("No route registered for callback query.")
            if self.handle_errors:
                await callback_query.answer(
                    text=self.no_action_found_error_message,
                    show_alert=self.alert_on_error,
                )
            return None

        return context
