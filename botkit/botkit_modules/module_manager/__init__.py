from haps import Inject
from pyrogram import Filters, Message

from botkit.core.moduleloader import ModuleLoader
from botkit.core.modules import Module
from .paged_module_view import PagedModuleView
from .view_models import ModuleInfo, ModuleInfosCollectionModel
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.services.companionbotservice import CompanionBotService
from botkit.views.renderer_client_mixin import PyroRendererClientMixin


class ModuleManagerModule(Module):
    module_loader: ModuleLoader = Inject()

    def __init__(self, user_client: PyroRendererClientMixin, bot_client: PyroRendererClientMixin):
        self.user_client = user_client
        self.bot_client = bot_client
        self.companion = CompanionBotService(user_client=user_client, bot_client=bot_client)

    def register(self, routes: RouteBuilder):
        with routes.using(self.user_client):
            routes.on(Filters.command("modules", prefixes=["#", "/"])).call(self.show_modules)

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
            routes.on_action("disable").mutate(self.disable_module).then_update(PagedModuleView)
            routes.on_action("enable").mutate(self.enable_module).then_update(PagedModuleView)

    async def show_modules(self, client: PyroRendererClientMixin, message: Message) -> None:
        await self.companion.send_view_via(
            message.chat.id,
            PagedModuleView(
                ModuleInfosCollectionModel(
                    all_items=[
                        ModuleInfo.from_module(m, self.module_loader)
                        for m in self.module_loader.modules
                        if m.route_collection
                    ]
                )
            ),
        )

    async def enable_module(self, module_info: ModuleInfosCollectionModel):
        module_to_enable = module_info.page_items[0]
        module_name = module_to_enable.name
        module = self.module_loader.get_module_by_name(module_name)
        await self.module_loader.register_module(module)
        module_to_enable.is_enabled = True
        return module_info

    async def disable_module(self, module_info: ModuleInfosCollectionModel):
        module_to_disable = module_info.page_items[0]
        module_name = module_to_disable.name
        module = self.module_loader.get_module_by_name(module_name)
        await self.module_loader.unregister_module(module)
        module_to_disable.is_enabled = False
        return module_info
