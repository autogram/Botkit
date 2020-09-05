import asyncio
import logging
import signal
from abc import ABCMeta, abstractmethod
from asyncio.events import AbstractEventLoop
from haps import base, Inject
from haps.application import Application
from logzero import logger as log
from pyrogram import Client as PyrogramClient
from typing import TYPE_CHECKING

try:
    from telethon import TelegramClient as TelethonClient
except:
    TelethonClient = None

from typing import List, Union, TYPE_CHECKING

from botkit.core.moduleloader import ModuleLoader
from botkit.core.modules._module import Module
from botkit.tghelpers.names import user_or_display_name
from abc import ABC


Client = Union[PyrogramClient, TelethonClient]


@base
class Startup(Application, ABC):
    module_loader: ModuleLoader = Inject()

    def __init__(self, clients: List[Client]):
        if not clients:
            raise ValueError("Must pass at least one client for initialization.")
        self.clients = clients

    @abstractmethod
    async def run_startup_tasks(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass

    async def _start_clients(self):
        log.debug("Starting clients...")
        start_tasks = (self.__start_client(c) for c in self.clients)
        await asyncio.gather(*start_tasks)

    async def __start_client(self, client):
        session_path = (
            client.session_name
            if hasattr(client, "session_name")
            else client.session.filename
        )

        log.debug(f"Starting session " f"{session_path}...")
        await client.start()
        me = await client.get_me()
        log.info(f"Started {user_or_display_name(me)} as {client.__class__.__name__}.")

    def run(self) -> None:
        log.debug("Autodiscovery completed. Initializing...")
        loop = asyncio.get_event_loop()

        try:
            signals = [signal.SIGTERM, signal.SIGINT]
            for s in signals:
                loop.add_signal_handler(
                    s, lambda s=s: asyncio.create_task(self._shutdown(loop))
                )
        except NotImplementedError:
            pass  # Windows does not implement signals

        loop.run_until_complete(self._start_async())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self._shutdown(loop))
        finally:
            logging.info("Graceful shutdown.")
            loop.close()

    def get_extra_modules(self) -> List[Module]:
        return []

    async def _start_async(self):
        await self._start_clients()
        for m in self.get_extra_modules() or []:
            self.module_loader.add_module_without_activation(m)
        await self.module_loader.activate_enabled_modules()
        await self.run_startup_tasks()
        log.info("Ready.")

    async def _shutdown(self, loop: AbstractEventLoop):
        log.info("Shutting down...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        log.info(f"Cancelling {len(tasks)} running or outstanding tasks")
        await asyncio.gather(*tasks)
        await self.on_shutdown()
        log.info("Graceful shutdown complete. Goodbye")
        loop.stop()
