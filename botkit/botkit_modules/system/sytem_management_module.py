from dataclasses import dataclass

import asyncio
from buslane.commands import Command, CommandHandler
from haps import Inject, Container
from pyrogram import filters
from pyrogram.types import Message, User
from typing import Optional, List, Any, Literal

from botkit.botkit_modules.system.system_tests import notests
from botkit.libraries.annotations import IClient
from botkit.persistence.callback_manager import (
    RedisCallbackManager,
    ICallbackManager,
)
from botkit.core.moduleloader import ModuleLoader
from botkit.core.modules._module import Module
from botkit.botkit_services.eventing import command_bus
from botkit.routing.route_builder.builder import RouteBuilder


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

    def __init__(self, user_client: IClient) -> None:
        self.user_client = user_client

        self.system_paused: bool = False
        self.paused_modules: Optional[List[Module]] = None

    async def load(self) -> _LoadCtx:
        return _LoadCtx(user_client_id=(await self.user_client.get_me()).id)

    def register(self, routes: RouteBuilder):
        routes.use(self.user_client)

        restart_command = filters.command("r", prefixes=[".", "#"]) | filters.command("restart")
        only_owner = filters.user(routes.context.load_result.user_client_id)

        routes.on(restart_command & only_owner).call(self.restart_system)

        routes.on(filters.command(["off", "pause"]) & only_owner).call(self.handle_pause_command)
        routes.on(filters.command(["on", "unpause"]) & only_owner).call(
            self.handle_unpause_command
        )

        command_bus.register(_ToggleSystemStateCommandHandler(self))

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
            if self.module_loader.is_active(x)
            and not self.module_loader.is_disabled(x)
            and not isinstance(x, type(self))
        ]
        self.log.info(
            f"Pausing modules:\n" + "\n".join([m.get_name() for m in loaded_modules]) + "\n..."
        )
        tasks = [self.module_loader.unregister_module(m) for m in loaded_modules]
        await asyncio.gather(*tasks, return_exceptions=True)
        self.system_paused = True
        self.paused_modules = loaded_modules

        try:
            callback_manager: RedisCallbackManager = Container().get_object(
                ICallbackManager, "redis"
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
                await self.module_loader.try_register_module(m)
        else:
            self.log.error(
                f"For some reason there were no paused modules: {self.paused_modules}. "
                f"Restarting with all modules instead."
            )
            await self.module_loader.register_enabled_modules()

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
