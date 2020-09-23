import asyncio
from asyncio import CancelledError
from typing import Callable, Coroutine, Dict, Iterable, List, Optional

from haps import Container, Inject
from haps.config import Configuration

from botkit.builtin_services.options.base import IOptionStore
from botkit.core.services import service
from botkit.dispatching.dispatcher import BotkitDispatcher
from botkit.utils.botkit_logging.setup import create_logger
from botkit.core.modules._module import Module
from ._hmr import HotModuleReloadWorker
from ._module_activator import ModuleActivator
from ._module_status import ModuleStatus

log = create_logger("module_loader")

DISABLED_MODULES = [
    "GameModule",
    "FunctionsBasedModule",
    "ReceiverModule",
    # belong together
    "ConversationMirrorModule",
    "ReplyModule",
    "Html5GameModule",
    # end
    "NotionCollectorModule",
]


@service
class ModuleLoader:
    # options: IOptionStore = Inject()
    activator: ModuleActivator = Inject()
    _hmr_worker: HotModuleReloadWorker = Inject()

    def __init__(self) -> None:
        self.log = create_logger("module_loader")

        discovered_modules: List[Module] = Configuration().get_var("modules")
        self.log.debug(f"{len(discovered_modules)} modules discovered.")

        self.__module_statuses: Dict[Module, ModuleStatus] = {
            m: ModuleStatus.disabled if m.get_name() in DISABLED_MODULES else ModuleStatus.inactive
            for m in discovered_modules
        }

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
            module.index = n + 1
            tasks.append(self.try_activate_module_async(module))

        await asyncio.gather(*tasks)

        self._hmr_worker.start(self.modules)

    async def try_activate_module_async(self, module: Module) -> None:
        if module not in self.__module_statuses:
            self.add_module_without_activation(module)

        try:
            if self.get_module_status(module) == ModuleStatus.disabled:
                self.log.debug(f"{module.get_name()} is disabled.")
                module.route_collection = []
                return
            if self.get_module_status(module) == ModuleStatus.active:
                raise ValueError(
                    f"Nothing to do as the module '{module.get_name()}' is already active."
                )

            result: ModuleStatus = await self.activator.activate_module_async(module)
            self.__module_statuses[module] = result
            # TODO: maybe add a log message in which view_state the module now is (especially when failed)
        except:
            self.log.exception(f"Could not load {module.get_name()}.")

    def get_module_status(self, module: Module) -> ModuleStatus:
        return self.__module_statuses[module]

    async def deactivate_module_async(self, module: Module):
        # TODO: Somehow find out which components to deactivate!
        if self.get_module_status(module) != ModuleStatus.active:
            raise ValueError("Cannot unregister as the module is not loaded.")

        try:
            await module.unload()
        except CancelledError:
            pass
        except:
            self.log.exception(f"Could not unload module {module.get_name()}.")

        try:
            # TODO: prettify
            dispatcher = Container().get_object(BotkitDispatcher)
            await dispatcher.remove_module_routes(module)
        except:
            self.log.exception(f"Could not remove routes of module {module.get_name()}.")

        self.__module_statuses[module] = ModuleStatus.inactive


# def run_validation_experiment(modules: Iterable[Module]):
#     render_funcs = get_view_renderers(modules)
#
#     for view in render_funcs:
#         try:
#             print("=" * 120)
#             print(inspect.getsource(view)[:600])
#             mocked_state = MagicMock()
#             mocked_state.__iter__.return_value = [mocked_state, mocked_state]
#             cbm = MemoryDictCallbackManager()
#
#             if quacks_like_view_render_func(view):
#                 rendered = render_functional_view(view, mocked_state, cbm)
#             else:
#                 continue
#                 rendered = view(mocked_state).render()
#
#             if rendered.inline_buttons:
#                 buttons = list(flatten(map(flatten, rendered.inline_buttons)))
#             else:
#                 buttons = []
#             callbacks = [cbm.lookup_callback(x.callback_data) for x in buttons]
#             print(callbacks)
#         except:
#             log.exception("lala", stacklevel=1)


def get_view_renderers(modules: Iterable[Module]) -> Iterable[Callable]:
    for m in modules:
        if not m.route_collection:
            continue
        for routes in m.route_collection.routes_by_client.values():
            for route in routes:
                if not route.plan._view:
                    continue
                yield route.plan._view.view
