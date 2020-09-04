import asyncio
from enum import Enum, auto
from typing import Any, Coroutine, Dict, Iterable, List, Optional, Type

import logzero
from haps import Inject
from haps.config import Configuration
from logzero import logger as log

from botkit.builtin_services.options.base import IOptionStore
from botkit.builtin_services.services import service
from botkit.core.hmr import HotModuleReloadWorker
from botkit.core.modules._module import Module
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


class ModuleStatus(Enum):
    inactive = auto()
    active = auto()
    disabled = auto()
    failed = auto()


@service
class ModuleLoader:
    options: IOptionStore = Inject()

    def __init__(self) -> None:
        self.log = logzero.setup_logger(ModuleLoader.__class__.__name__)

        self.route_builder_class = RouteBuilder
        self.dispatcher = BotkitDispatcher()

        discovered_modules: List[Module] = Configuration().get_var("modules")

        self.__module_statuses: Dict[Module, ModuleStatus] = {
            m: ModuleStatus.disabled if m.get_name() in DISABLED_MODULES else ModuleStatus.inactive
            for m in discovered_modules
        }

        self._hmr_worker = HotModuleReloadWorker()

    @property
    def modules(self) -> Iterable[Module]:
        return self.__module_statuses.keys()

    @property
    def active_modules(self) -> Iterable[Module]:
        return (m for m, s in self.__module_statuses.items() if s == ModuleStatus.active)

    def add_module_without_activation(self, module: Module) -> None:
        self.__module_statuses[module] = ModuleStatus.inactive

    def get_module_by_name(self, name: str) -> Optional[Module]:
        return next((m for m in self.modules if m.get_name() == name), None)

    async def activate_enabled_modules(self) -> None:
        tasks: List[Coroutine] = []
        for n, module in enumerate(self.modules):
            module.group_index = n + 1
            tasks.append(self.try_activate_module(module))

        await asyncio.gather(*tasks)

        self._hmr_worker.start(self.modules)

    async def try_activate_module(self, module: Module) -> None:
        if module not in self.__module_statuses:
            self.add_module_without_activation(module)

        try:
            if self.get_module_status(module) == ModuleStatus.disabled:
                log.debug(f"{module.get_name()} is disabled.")
                module.route_collection = []
                return
            if self.get_module_status(module) == ModuleStatus.active:
                raise ValueError("Nothing to register as the module is already active.")

            return await self._activate_module_or_fail(module)
        except:
            log.exception(f"Could not load {module.get_name()}.")

    async def _activate_module_or_fail(self, module: Module) -> None:
        assert module.group_index is not None

        async def rollback() -> None:
            self.__module_statuses[module] = ModuleStatus.failed
            try:
                await module.unload()
            except:
                pass

        try:
            load_result = await module.load()
        except Exception as e:
            log.exception(
                f"Calling `load()` on {module.get_name()} failed and the module will not be initialized."
            )
            await rollback()
            raise e

        try:
            route_collection = self.build_module_routes(
                self.route_builder_class, module, load_result
            )
            module.route_collection = route_collection

            await self.dispatcher.add_module_routes(module)
        except Exception as e:
            log.exception(f"Could not build module routes for module {module.get_name()}.")
            await rollback()
            raise e

        self.__module_statuses[module] = ModuleStatus.active

    @staticmethod
    def build_module_routes(
        route_builder_class: Type[RouteBuilder], module: Module, load_result: Any = None
    ) -> RouteCollection:
        route_builder = route_builder_class(context=RouteBuilderContext(load_result=load_result))
        module.register(route_builder)
        return route_builder._route_collection

    async def unregister_module(self, module: Module):
        if self.get_module_status(module) != ModuleStatus.active:
            raise ValueError("Cannot unregister as the module is not loaded.")

        try:
            await module.unload()
        except:
            self.log.exception(f"Could not unload module {module.get_name()}.")

        try:
            await self.dispatcher.remove_module_routes(module)
        except:
            self.log.exception(f"Could not remove routes of module {module.get_name()}.")

        self.__module_statuses[module] = ModuleStatus.inactive

        # if not any((bool(x) for x in client.dispatcher.groups.values())):
        #     print(
        #         "A client could be shut down, but that logic is not implemented yet."
        #     )

    def get_module_status(self, module: Module) -> ModuleStatus:
        return self.__module_statuses[module]
