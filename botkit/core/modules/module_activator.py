"""
TODO: Refactor moduleloader:
- Take out the _activate_module_or_fail method
- Take out the deactive_module method
- Report back the new status of the module
"""
from asyncio.exceptions import CancelledError
from typing import Any, Type

from haps import Container, inject, base, egg, scope, SINGLETON_SCOPE
from logzero import logger as log

from botkit.core.modules import Module
from botkit.core.modules.module_status import ModuleStatus
from botkit.dispatching.dispatcher import BotkitDispatcher
from botkit.routing.route_builder.builder import RouteBuilder, RouteBuilderContext
from botkit.routing.route_builder.route_collection import RouteCollection
from botkit.settings import botkit_settings


@base
@egg
@scope(SINGLETON_SCOPE)
class ModuleActivator:
    def __init__(self, dispatcher: BotkitDispatcher = None):
        self.dispatcher = dispatcher or Container().get_object(BotkitDispatcher)
        self.route_builder_class: Type[
            RouteBuilder
        ] = botkit_settings.route_builder_class or RouteBuilder

    async def activate_module_async(self, module: Module) -> ModuleStatus:

        # TODO: This should probably also activate components, but it's a little unclear what should happen
        # when an instance of a component appears to be added to multiple modules. Should it be unloaded when
        # *any* of the utilizing modules fails?

        assert module.index is not None

        async def rollback():
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

        return ModuleStatus.active

    @classmethod
    def build_module_routes(
        cls, route_builder_class: Type[RouteBuilder], module: Module, load_result: Any = None
    ) -> RouteCollection:
        route_builder = route_builder_class(context=RouteBuilderContext(load_result=load_result))
        module.register(route_builder)
        route_collection = route_builder._route_collection
        cls._register_components(route_builder, route_collection)
        return route_collection

    @classmethod
    def _register_components(cls, route_builder: RouteBuilder, collection: RouteCollection):
        for client, components in collection.components_by_client.items():
            for comp in components:
                if not comp._is_registered:
                    comp.register(route_builder)
                    comp._is_registered = True

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
            await self.dispatcher.remove_module_routes(module)
        except:
            self.log.exception(f"Could not remove routes of module {module.get_name()}.")

        self.__module_statuses[module] = ModuleStatus.inactive

        # if not any((bool(x) for x in client.dispatcher.groups.values())):
        #     print(
        #         "A client could be shut down, but that logic is not implemented yet."
        #     )
