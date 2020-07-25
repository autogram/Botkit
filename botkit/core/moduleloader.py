import traceback

import asyncio

from haps import Inject
from haps.config import Config
from logzero import logger as log
from typing import Any, List, Coroutine, Optional, Type

from botkit.core.modules._module import Module
from botkit.botkit_services.services import service
from botkit.botkit_services.options.base import IOptionStore
from botkit.dispatching.dispatcher import BotkitDispatcher
from botkit.routing.route_builder.builder import RouteBuilder, RouteBuilderContext
from botkit.routing.route_builder.route_collection import RouteCollection

DISABLED_MODULES = [
    "GameModule",
    "FunctionsBasedModule",
    "ReceiverModule",
    # belong together
    "IncomingMessagesModule",
    "ReplyModule",
    # end
    "NotionCollectorModule",
]

# noinspection PyMethodMayBeStatic

# DisabledModules = ListOption(
#     name="disabled_modules", description="List of modules that should be ignored on system " "start", default_value=[],
# )


@service
class ModuleLoader:
    modules: List[Module] = Config("modules")
    options: IOptionStore = Inject()

    def __init__(self) -> None:
        self.route_builder_class = RouteBuilder
        self.dispatcher = BotkitDispatcher()

    def get_module_by_name(self, name: str) -> Optional[Module]:
        return next((m for m in self.modules if m.get_name() == name), None)

    async def register_enabled_modules(self) -> None:
        tasks: List[Coroutine] = []
        for n, module in enumerate(self.modules):
            module.group_index = n
            tasks.append(self.register_module(module))

        results = await asyncio.gather(*tasks)

    async def register_module(self, module: Module) -> None:
        try:
            if self.is_disabled(module):
                log.debug(f"{module.get_name()} is disabled.")
                module.route_collection = []
                return
            if self.is_active(module):
                raise ValueError("Nothing to register as the module is already active.")

            return await self._register_module_or_fail(module)
        except:
            log.exception(f"Could not load {module.get_name()}.")

    async def _register_module_or_fail(self, module: Module) -> None:
        assert module.group_index is not None

        try:
            load_result = await module.load()
        except Exception as e:
            log.error(
                f"Calling `load()` on {module.get_name()} failed with {e.__class__.__name__}. Skipping module "
                f"initialization..."
            )
            traceback.print_exc()
            return

        route_collection = self.build_module_routes(self.route_builder_class, module, load_result)
        module.route_collection = route_collection

        await self.dispatcher.add_module_routes(module)

    @staticmethod
    def build_module_routes(
        route_builder_class: Type[RouteBuilder], module: Module, load_result: Any = None
    ) -> RouteCollection:
        route_builder = route_builder_class(
            # Attach result of `.load()` so that the synchronous `register` method has access to data only
            # retrievable in an asynchronous coroutine.
            context=RouteBuilderContext(load_result=load_result)
        )
        module.register(route_builder)

        route_collection: RouteCollection = route_builder._route_collection

        return route_collection

    async def unregister_module(self, module: Module):
        if not self.is_active(module):
            raise ValueError("Cannot unregister as the module is not loaded.")

        await module.unload()

        await self.dispatcher.remove_module_routes(module)

        assert not self.is_active(module)

        # if not any((bool(x) for x in client.dispatcher.groups.values())):
        #     print(
        #         "A client could be shut down, but that logic is not implemented yet."
        #     )

    def is_active(self, module: Module) -> bool:
        return self.dispatcher.is_registered(module)

    def is_disabled(self, module: Module) -> bool:
        name = module.get_name()
        # return self.options.get_global_value()
        return name in DISABLED_MODULES  # TODO: get from settings
