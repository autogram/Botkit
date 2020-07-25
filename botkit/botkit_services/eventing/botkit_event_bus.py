import asyncio

import inspect

import logging
from buslane.commands import CommandBus, Command, CommandHandler
from buslane.events import EventBus, EventHandler, Event
from botkit.botkit_services.services import service


@service
class BotkitEventBus(EventBus):
    def __init__(self) -> None:
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)

    def handle(self, event: Event, handler: EventHandler) -> None:
        self.log.info(f"Handling event {event} by {handler}")
        res = handler.handle(event)
        if inspect.isawaitable(res):
            asyncio.ensure_future(res)


@service
class BotkitCommandBus(CommandBus):
    def __init__(self) -> None:
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)

    def handle(self, command: Command, handler: CommandHandler) -> None:
        self.log.info(f"Handling event {command} by {handler}")
        res = handler.handle(command)
        if inspect.isawaitable(res):
            asyncio.ensure_future(res)
