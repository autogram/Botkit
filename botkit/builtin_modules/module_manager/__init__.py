from haps import Inject
from pyrogram.filters import command

from botkit.core.moduleloader import ModuleLoader
from botkit.core.modules import Module
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.services.companionbotservice import CompanionBotService
from .paged_module_view import PagedModuleView
from .view_models import ModuleInfo, ModuleInfosCollectionModel
from ...types.client import IClient


class ModuleManagerModule(Module):
    module_loader: ModuleLoader = Inject()

    def __init__(self, user_client: IClient, bot_client: IClient):
        self.user_client = user_client
        self.bot_client = bot_client
        self.companion = CompanionBotService(
            user_client=user_client, bot_client=bot_client
        )

    def register(self, routes: RouteBuilder):
        with routes.using(self.user_client):
            (
                routes.on(command("modules", prefixes=["#", "/"]))
                .gather(self.get_modules)
                .then_send(PagedModuleView, via=self.bot_client)
            )

        with routes.using(self.bot_client):
            (
                routes.on_action("page_back")
                .mutate(ModuleInfosCollectionModel.flip_previous_page)
                .then_update(PagedModuleView)
            )
            (
                routes.on_action("page_forward")
                .mutate(ModuleInfosCollectionModel.flip_next_page)
                .then_update(PagedModuleView)
            )
            (
                routes.on_action("deactivate")
                .mutate(self.deactivate_module)
                .then_update(PagedModuleView)
            )
            (
                routes.on_action("activate")
                .mutate(self.activate_module)
                .then_update(PagedModuleView)
            )

    def get_modules(self) -> ModuleInfosCollectionModel:
        return ModuleInfosCollectionModel(
            all_items=[
                ModuleInfo.from_module(m, self.module_loader)
                for m in self.module_loader.modules
                if m.route_collection
            ]
        )

    async def activate_module(self, module_info: ModuleInfosCollectionModel):
        module_to_enable = module_info.page_items[0]
        module_name = module_to_enable.name
        module = self.module_loader.get_module_by_name(module_name)
        await self.module_loader.try_activate_module(module)
        module_to_enable.module_state = self.module_loader.get_module_status(module)
        return module_info

    async def deactivate_module(self, module_info: ModuleInfosCollectionModel):
        module_to_disable = module_info.page_items[0]
        module_name = module_to_disable.name
        module = self.module_loader.get_module_by_name(module_name)
        await self.module_loader.unregister_module(module)
        module_to_disable.module_state = self.module_loader.get_module_status(module)
        return module_info
