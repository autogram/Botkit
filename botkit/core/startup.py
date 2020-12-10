import asyncio
import logging
import signal
from abc import abstractmethod
from asyncio.events import AbstractEventLoop

from haps import Inject, base
from haps.application import Application
from injector import Injector, inject
from pyrogram import Client as PyrogramClient

from botkit.configuration import ClientConfig
from botkit.core.modules import activation
from botkit.core.modules.activation import ModuleLoader, configure_module_activation
from botkit.clients.client import IClient
from botkit.utils.botkit_logging.setup import create_logger

try:
    # noinspection PyUnresolvedReferences
    from telethon import TelegramClient as TelethonClient
except:
    TelethonClient = None

from typing import Any, List, Union

from botkit.core.modules._module import Module
from botkit.tghelpers.names import user_or_display_name
from abc import ABC

Client = Union[PyrogramClient, TelethonClient]


@base
class Startup(Application, ABC):
    def __init__(self, clients: List[Client], module_loader: ModuleLoader = None):
        if not clients:
            raise ValueError("Must pass at least one client for initialization.")
        self.clients = clients

        self.module_loader = module_loader or Injector(configure_module_activation).get(
            ModuleLoader
        )

        self.log = create_logger("startup")

    @abstractmethod
    async def run_startup_tasks(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass

    async def _start_clients(self):
        self.log.debug("Starting clients...")
        start_tasks = (self.__start_client(c) for c in self.clients)
        await asyncio.gather(*start_tasks)

    async def _stop_clients(self):
        self.log.debug("Starting clients...")
        start_tasks = (self.__stop_client(c) for c in self.clients)
        await asyncio.gather(*start_tasks)

    async def __start_client(self, client: Union[IClient, Any]):
        # TODO(XXX): This forces the client instances to have a `config` property, which is not reflected in `IClient`.
        self.log.info(f"Starting {client.__class__.__name__}, {client.config.description}...")
        kwargs = client.config.start_kwargs()
        await client.start(**kwargs)

        me = await client.get_me()
        client.own_user_id = me.id
        client.own_username = me.username

        self.log.info(f"Started {user_or_display_name(me)} as {client.__class__.__name__}.")

    async def __stop_client(self, client: Union[IClient, Any]):
        self.log.info(f"Stopping {client.__class__.__name__}, {client.config.description}...")
        await client.stop()
        self.log.info(f"Stopped {client.__class__.__name__}.")

    def run(self, loop: AbstractEventLoop = None) -> None:
        self.log.debug("Initializing...")
        loop = loop or asyncio.get_event_loop()

        try:
            signals = [signal.SIGTERM, signal.SIGINT]
            for s in signals:
                loop.add_signal_handler(s, lambda s=s: asyncio.create_task(self._shutdown(loop)))
        except NotImplementedError:
            pass  # Windows does not implement signals

        loop.run_until_complete(self._start_async())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(self._shutdown(loop))
            logging.info("Graceful shutdown.")
            loop.close()

    def get_extra_modules(self) -> List[Module]:
        return []

    async def _start_async(self):
        await self._start_clients()
        for m in self.get_extra_modules() or []:
            self.module_loader.add_module_without_activation(m)
        self.log.debug("Activating modules")
        await self.module_loader.activate_enabled_modules()
        self.log.debug("Running startup tasks")
        await self.run_startup_tasks()
        self.log.info("Ready.")

    async def _shutdown(self, loop: AbstractEventLoop):
        self.log.info("Shutting down...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        self.log.info(f"Cancelling {len(tasks)} running or outstanding tasks")
        await asyncio.gather(*tasks)
        await self.on_shutdown()
        self.log.info("Graceful shutdown complete. Goodbye")
        loop.stop()
