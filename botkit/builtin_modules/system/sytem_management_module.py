import logging
from dataclasses import dataclass

import asyncio
from buslane.commands import Command, CommandHandler
from haps import Inject, Container
from pyrogram import filters
from pyrogram.types import Message
from typing import Optional, List, Any, Literal

from botkit.builders import ViewBuilder
from botkit.builtin_modules.system.system_tests import notests
from botkit.core.modules.activation import ModuleLoader, ModuleStatus
from botkit.libraries.annotations import IClient
from botkit.persistence.callback_store import (
    RedisCallbackManager,
    CallbackStoreBase,
)
from botkit.core.modules._module import Module
from botkit.builtin_services.eventing import command_bus
from botkit.routing.pipelines.execution_plan import SendTo
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.settings import botkit_settings
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context

log = create_logger("system_management_module", use_standard_format=False)


@dataclass
class _LoadCtx:
    user_client_id: int


@dataclass
class ToggleSystemStateCommand(Command):
    new_state: Literal["pause", "unpause"]
    triggered_by: Any
    reason_phrase: str


class SystemManagementModule(Module):
    module_loader: ModuleLoader = Inject()

    def __init__(self, user_client: IClient, bot_client: Optional[IClient] = None) -> None:
        self.user_client = user_client
        self.bot_client = bot_client

        self.system_paused: bool = False
        self.paused_modules: Optional[List[Module]] = None

    async def load(self) -> _LoadCtx:
        return _LoadCtx(user_client_id=(await self.user_client.get_me()).id)

    def register(self, routes: RouteBuilder):
        command_bus.register(_ToggleSystemStateCommandHandler(self))

        restart_command = filters.command("r", prefixes=[".", "#"]) | filters.command("restart")
        only_owner = filters.user(routes.context.load_result.user_client_id)

        with routes.using(self.user_client):
            routes.on(restart_command & only_owner).call(self.restart_system)

            routes.on(filters.command(["off", "pause"]) & only_owner).call(
                self.handle_pause_command
            )
            routes.on(filters.command(["on", "unpause"]) & only_owner).call(
                self.handle_unpause_command
            )

            routes.on(filters.command("error") & only_owner).call(raise_error)

            (
                routes.on(filters.command(["log", "logging", "level", "loglevel"]) & only_owner)
                .gather(LogSettings)
                .remove_trigger()
                .then_send(
                    log_settings_view,
                    via_bot=self.bot_client or None,
                    to=SendTo.same_chat_quote_replied_to,
                )
            )

        if self.bot_client:
            with routes.using(self.bot_client):
                (
                    routes.on_action("select_log_level")
                    .mutate(LogSettings.set_global_botkit_log_level)
                    .then_update(log_settings_view)
                )
                # TODO: find nice abstraction
                # (routes.on_action("done").call(done))

    @staticmethod
    async def restart_system(_, message: Message):
        # TDOO: add notification
        await message.delete()
        command_bus.execute(
            ToggleSystemStateCommand(
                new_state="pause",
                triggered_by="user",
                reason_phrase="User requested restart of system.",
            )
        )
        await asyncio.sleep(2)
        command_bus.execute(
            ToggleSystemStateCommand(
                new_state="unpause", triggered_by="user", reason_phrase="Starting back up.",
            )
        )

    @notests
    async def handle_pause_command(self, _client, message: Message):
        await message.delete()
        if self.system_paused:
            await message.reply("System is already paused. Send /on to continue.")
            return
        await self.pause_system()
        await message.reply("Bot paused.")

    async def pause_system(self):
        loaded_modules = [
            x
            for x in self.module_loader.modules
            if self.module_loader.get_module_status(x) == ModuleStatus.active
            and not isinstance(x, type(self))
        ]
        self.log.info(
            f"Pausing modules:\n" + "\n".join([m.get_name() for m in loaded_modules]) + "\n..."
        )
        tasks = [self.module_loader.deactivate_module_async(m) for m in loaded_modules]
        await asyncio.gather(*tasks, return_exceptions=True)
        self.system_paused = True
        self.paused_modules = loaded_modules

        try:
            callback_manager: RedisCallbackManager = Container().get_object(
                CallbackStoreBase, "redis"
            )
            callback_manager.callbacks.sync()
            self.log.info("Callbacks synced.")
        except:
            self.log.exception("Error while synchronizing callback manager states.")

        self.log.info("System paused.")

    async def handle_unpause_command(self, _client, message: Message):
        await message.delete()
        if not self.system_paused:
            await message.reply("System is not paused.")
            return
        await self.unpause_system()
        await message.reply("System unpaused.")

    async def unpause_system(self):
        if self.paused_modules:
            self.log.info(f"Unpausing {len(self.paused_modules)} modules...")
            for m in self.paused_modules:
                await self.module_loader.try_activate_module_async(m)
        else:
            self.log.error(
                f"For some reason there were no paused modules: {self.paused_modules}. "
                f"Restarting with all modules instead."
            )
            await self.module_loader.activate_enabled_modules()

        self.log.info("System unpaused.")
        self.system_paused = False


class _ToggleSystemStateCommandHandler(CommandHandler[ToggleSystemStateCommand]):
    def __init__(self, sys_module: SystemManagementModule):
        self.sys_module = sys_module

    async def handle(self, command: ToggleSystemStateCommand) -> None:
        self.sys_module.log.info(
            f"{command.triggered_by} issues system to *{command.new_state}*. Reason: {command.reason_phrase}"
        )
        if command.new_state == "pause":
            await self.sys_module.pause_system()
        elif command.new_state == "unpause":
            await self.sys_module.unpause_system()


@dataclass  # TODO: don't gather this
class LogSettings:
    ALL_LEVELS = {
        logging.DEBUG: "Debug",
        logging.INFO: "Info",
        logging.WARNING: "Warning",
        logging.ERROR: "Error",
    }

    @property
    def current_level(self) -> int:
        return botkit_settings.log_level

    def set_global_botkit_log_level(self, ctx: Context):
        log.info(f"Botkit log level changed to {ctx.payload}")
        botkit_settings.log_level = ctx.payload

    def get_level_name(self, level: int) -> str:
        return self.ALL_LEVELS.get(level, "Unknown")


def log_settings_view(state: LogSettings, builder: ViewBuilder) -> None:
    (
        builder.html.br()
        .cta(f"Configure {botkit_settings.application_name} logging", end=None)
        .spc()
        .command("loglevel", end=None)
        .para()
        .text("Current log level:")
        .spc()
        .italic(state.get_level_name(state.current_level))
    )

    # Menu will not be rendered if no bot client is set up
    for n, (level, name) in enumerate(state.ALL_LEVELS.items()):
        # https://fsymbols.com/signs/arrow/
        caption = f"➤ {name}" if level == state.current_level else name
        builder.menu.rows[n].action_button(
            caption, "select_log_level", level, notification=f"Global log level set to {name}.",
        )

    builder.menu.rows[99].action_button("Done ✅", "done")


async def raise_error(_, message: Message):
    raise Exception("This is a test exception to test logging")
