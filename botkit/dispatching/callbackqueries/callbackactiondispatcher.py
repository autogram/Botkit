import asyncio
from typing import Any, Dict, Optional, Union

from cached_property import cached_property
from haps import Container
from logzero import logger as log
from pyrogram import CallbackQuery, CallbackQueryHandler, Update
from pyrogram.client.filters.filters import create

from botkit.dispatching.callbackqueries.callback_manager import CallbackActionContext, ICallbackManager
from botkit.routing.route import RouteDefinition, RouteHandler
from botkit.routing.triggers import ActionIdTypes
from botkit.settings import botkit_settings
from botkit.types.client import IClient
from botkit.views.botkit_context import BotkitContext


class CallbackActionDispatcher:
    def __init__(self, alert_on_error: bool = True):
        self._action_routes: Dict[ActionIdTypes, RouteHandler] = dict()

        self.alert_on_error = alert_on_error

        self.bot_restarted_error_message = (
            "Sorry, looks like the bot has been restarted in the meantime "
            "and doesn't know what you clicked on. Please start over!"
        )

    def add_action_route(self, route: RouteHandler):
        assert route.action_id is not None
        self._action_routes[route.action_id] = route

    @property
    def pyrogram_handler(self) -> CallbackQueryHandler:
        game_callback_filter = create(lambda _, cbq: bool(cbq.game_short_name), "GameCallbackQuery")
        return CallbackQueryHandler(self.handle, filters=~game_callback_filter)

    @staticmethod
    def check(update: Update, route: RouteDefinition):
        return route.triggers.filters(update) if callable(route.triggers.filters) else True

    async def handle(self, client: IClient, callback_query: CallbackQuery) -> Union[bool, Any]:
        cb_ctx: Optional[CallbackActionContext] = await self._get_context_or_respond(callback_query)
        if not cb_ctx:
            return False

        route = self._action_routes[cb_ctx.action]

        botkit_context: BotkitContext = BotkitContext(
            client=client, update=callback_query, state=cb_ctx.state, _action=cb_ctx.action, _payload=cb_ctx.payload
        )

        try:
            # TODO: Time out after a few seconds (maybe 3)
            tasks = []
            if cb_ctx.notification:
                tasks.append(callback_query.answer(cb_ctx.notification, show_alert=cb_ctx.show_alert))

            # noinspection PyTypeChecker
            result = asyncio.create_task(route.callback(client, callback_query, botkit_context))
            tasks.append(result)
            await asyncio.gather(*tasks)
            return result.result()
        except:
            log.exception(f"A handler failed: {route.description}")
            await callback_query.answer(text="Sorry, something went wrong.", show_alert=False)
            return False

    @cached_property
    def callback_manager(self) -> ICallbackManager:
        return Container().get_object(ICallbackManager, botkit_settings.callback_manager_qualifier)

    async def _get_context_or_respond(self, callback_query: CallbackQuery) -> Optional[CallbackActionContext]:
        context = self.callback_manager.lookup_callback(callback_query.data)

        if not context:
            log.error("Could not find a callback query context.")
            if self.alert_on_error:
                await callback_query.answer(text=self.bot_restarted_error_message, show_alert=True)
            return None

        if context.action not in self._action_routes:
            return None

        return context
