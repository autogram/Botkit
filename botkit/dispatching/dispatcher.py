from logging import Logger
from typing import Any, Dict, List, Union

from haps import SINGLETON_SCOPE, base, egg, scope
from pyrogram import Client
from pyrogram.handlers.handler import Handler
from typing_extensions import Literal

from botkit.dispatching.callbackqueryactiondispatcher import CallbackQueryActionDispatcher
from botkit.core.modules import Module
from botkit.dispatching.deeplinkstartactiondispatcher import DeepLinkStartActionDispatcher
from botkit.routing.route import RouteHandler
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient
from botkit.utils.botkit_logging.setup import create_logger


"""
Indicates where the evaluation of individual updates takes place
"""
# noinspection PydanticTypeChecker somehow Literals keep breaking PyCharm...
UPDATE_TYPE_HANDLING_SCOPE: Dict[UpdateType, Literal["global", "module"]] = {
    UpdateType.raw: "module",
    UpdateType.message: "module",
}


@base
@egg
@scope(SINGLETON_SCOPE)
class BotkitDispatcher:
    def __init__(self):
        self.callback_query_action_dispatchers: Dict[
            IClient, CallbackQueryActionDispatcher
        ] = dict()
        self.deep_link_start_action_dispatchers: Dict[
            IClient, DeepLinkStartActionDispatcher
        ] = dict()
        self._inline_query_factory: Any = None
        self.module_handlers: Dict[int, Dict[IClient, List[Handler]]] = dict()

        self.log: Logger = create_logger("dispatcher")

    async def add_module_routes(self, module: Module):
        log_msg = []

        for client, routes in module.route_collection.routes_by_client.items():
            for route in routes:
                for update_type, route_wrapper in route.handler_by_update_type.items():
                    await self.add_route_for_update_type(
                        module, client, update_type, route_wrapper
                    )

            """
            TODO: split this up into:
                - Fetches context
                - holds list of module_action_dispatchers
                - returns after first matching dispatcher
            - ModuleActionDispatcher(ModuleDispatcher)
                - Gets route and calls it

            Then do the same for QuickActions


            TODO:
            - Also unregister actions from CallbackActionDispatcher
            """

        self.log.info(
            f"({module.index}) {module.get_name()} loaded"
            + (" with: " + ", ".join(log_msg) if log_msg else "")
        )

    async def add_route_for_update_type(
        self,
        module_or_group: Union[int, Module],
        client: IClient,
        update_type: UpdateType,
        route_handler: RouteHandler,
    ):
        if isinstance(module_or_group, Module):
            assert module_or_group.index is not None
            group_index = module_or_group.index
        else:
            group_index = module_or_group

        if update_type == UpdateType.callback_query:
            if not route_handler.action_id:
                raise ValueError(
                    f"Route handler {route_handler} declares to be associated to callback queries "
                    f"but its action_id was None."
                )
            dp = await self._get_or_create_callback_query_action_dispatcher(client)
            dp.add_action_route(route_handler)

        elif update_type == UpdateType.message:
            if route_handler.action_id is not None:
                dp = await self._get_or_create_deep_link_start_action_dispatcher(client)
                dp.add_action_route(route_handler)
            else:
                await self.add_handler(group_index, client, route_handler.pyrogram_handler)

        elif update_type == UpdateType.raw:
            raise NotImplementedError("Cannot dispatch raw updates yet.")

        elif update_type == UpdateType.inline_query:
            raise NotImplementedError("Cannot dispatch inline queries yet.")

        elif update_type == UpdateType.poll:
            raise NotImplementedError("Cannot dispatch polls yet.")

        elif update_type == UpdateType.poll:
            raise NotImplementedError("Cannot dispatch user status updates yet.")

    async def remove_module_routes(self, module: Module):
        group = module.index

        if not (module_handlers := self.module_handlers.get(group)):
            self.log.info(f"No routes to remove for {module.get_name()}.")
            return

        for client, h in module_handlers.items():
            for handler in h:
                try:
                    # TODO(libs): Abstract
                    client.remove_handler(handler, group)
                except Exception:
                    self.log.exception(f"Could not remove handler {handler} from group {group}.")

        del self.module_handlers[group]

    async def add_handler(self, group: int, client: IClient, handler: Handler):
        assert group is not None
        assert client is not None
        assert handler is not None

        # TODO(libs): Abstract
        # async with client.dispatcher.locks_list[-1]:
        client.add_handler(handler, group)

        self.module_handlers.setdefault(group, {})
        self.module_handlers[group].setdefault(client, [])
        self.module_handlers[group][client].append(handler)

    def is_registered(self, module: Module) -> bool:
        return module.index in self.module_handlers

    async def _get_or_create_callback_query_action_dispatcher(
        self, client
    ) -> CallbackQueryActionDispatcher:
        # TODO: don't do this if it's a user client

        if not (action_dispatcher := self.callback_query_action_dispatchers.get(client)):
            self.callback_query_action_dispatchers[client] = (
                action_dispatcher := CallbackQueryActionDispatcher()
            )

            # All callback query handlers use the same group (only one of them applies for a given update)
            await self.add_handler(0, client, action_dispatcher.pyrogram_handler)

        return action_dispatcher

    async def _get_or_create_deep_link_start_action_dispatcher(
        self, client
    ) -> DeepLinkStartActionDispatcher:
        # TODO: don't do this if it's a user client

        if not (action_dispatcher := self.deep_link_start_action_dispatchers.get(client)):
            self.deep_link_start_action_dispatchers[client] = (
                action_dispatcher := DeepLinkStartActionDispatcher()
            )

            # All deep link handlers use the same group (only one of them applies for a given update)
            await self.add_handler(0, client, action_dispatcher.pyrogram_handler)

        return action_dispatcher
