from typing import Any, Dict, List, Union

import logzero
from pyrogram import Client
from pyrogram.handlers.handler import Handler
from typing_extensions import Literal

from botkit.dispatching.callbackqueries.callbackactiondispatcher import CallbackActionDispatcher
from botkit.core.modules import Module
from botkit.routing.route import RouteHandler
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient

"""
Indicates where the evaluation of individual updates takes place
"""
# noinspection PydanticTypeChecker somehow Literals keep breaking PyCharm...
UPDATE_TYPE_HANDLING_SCOPE: Dict[UpdateType, Literal["global", "module"]] = {
    UpdateType.raw: "module",
    UpdateType.message: "module",
}


class BotkitDispatcher:
    def __init__(self):
        self.callback_action_dispatchers: Dict[Client, CallbackActionDispatcher] = dict()
        self._inline_query_factory: Any = None
        self.module_handlers: Dict[int, Dict[Client, List[Handler]]] = dict()

        self.log = logzero.setup_logger(BotkitDispatcher.__name__)

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
            f"({module.group_index}) {module.get_name()} loaded"
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
            assert module_or_group.group_index is not None
            group_index = module_or_group.group_index
        else:
            group_index = module_or_group

        if update_type == UpdateType.raw:
            raise NotImplementedError("Cannot dispatch raw updates yet.")

        elif update_type == UpdateType.message:
            await self.add_handler(group_index, client, route_handler.pyrogram_handler)

        elif update_type == UpdateType.callback_query:
            (await self._get_or_create_action_dispatcher(client)).add_action_route(route_handler)

        elif update_type == UpdateType.inline_query:
            raise NotImplementedError("Cannot dispatch inline queries yet.")

        elif update_type == UpdateType.poll:
            raise NotImplementedError("Cannot dispatch polls yet.")

        elif update_type == UpdateType.poll:
            raise NotImplementedError("Cannot dispatch user status updates yet.")

    async def remove_module_routes(self, module: Module):
        group = module.group_index

        for client, h in self.module_handlers[group].items():
            for handler in h:
                try:
                    client.remove_handler(handler, group)
                except Exception:
                    self.log.exception(f"Could not remove handler {handler} from group {group}.")

        del self.module_handlers[group]

    async def add_handler(self, group: int, client: Client, handler: Handler):
        assert group is not None
        assert client is not None
        assert handler is not None

        async with client.dispatcher.locks_list[-1]:
            client.add_handler(handler, group)

            self.module_handlers.setdefault(group, {})
            self.module_handlers[group].setdefault(client, [])
            self.module_handlers[group][client].append(handler)

    def is_registered(self, module: Module) -> bool:
        return module.group_index in self.module_handlers

    async def _get_or_create_action_dispatcher(self, client) -> CallbackActionDispatcher:

        if not (action_dispatcher := self.callback_action_dispatchers.get(client)):
            self.callback_action_dispatchers[client] = (
                action_dispatcher := CallbackActionDispatcher()
            )

            # All callback queries use the same group (only one of them applies for a given update)
            await self.add_handler(0, client, action_dispatcher.pyrogram_handler)

        return action_dispatcher
