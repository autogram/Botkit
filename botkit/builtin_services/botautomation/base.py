from enum import IntEnum

import functools
import re
from abc import abstractmethod
from commons.core.base.controller import Controller
from commons.core.clients.userclient import IUserClient
from commons.coreservices.lookup.lookupservice import ILookupService
from haps import Inject
from telethon.events import NewMessage
from telethon.tl.custom import Conversation, Message, InlineResults
from telethon.tl.types.messages import BotCallbackAnswer
from typing import Dict, Callable, Any, Pattern


def notify_on_exception(func):
    @functools.wraps(func)
    async def wrapper(cls: Controller, event: NewMessage.Event):

        try:
            result = await func(cls, event)
        except UnexpectedBehaviorException as e:
            return await cls.use.notify_here(
                event.message_descriptor, e.message, Duration.ERROR_SHORT
            )

        return result

    return wrapper


class UnexpectedBehaviorException(Exception):
    def __init__(self, message, *args: object, **kwargs: object) -> None:
        self.message = message
        super().__init__(*args, **kwargs)


class Matcher(IntEnum):
    Equals = 1
    Startswith = 2
    Endswith = 3
    Contains = 4
    RegExSearch = 5
    RegExMatch = 6

    def match(self, text: str, query: str or Pattern):
        if self == self.Equals:
            return text.lower() == query.lower()
        elif self == self.Startswith:
            return text.lower().startswith(query.lower())
        elif self == self.Endswith:
            return text.lower().endswith(query.lower())
        elif self == self.Contains:
            return query.lower() in text.lower()
        elif self == self.RegExSearch:
            return bool(re.compile(query).search(text))
        elif self == self.RegExMatch:
            return bool(re.compile(query).match(text))


class BotAutomationBase(object):
    client: IUserClient = Inject()
    lookup: ILookupService = Inject()

    def __init__(self, default_timeout=10, total_timeout=60,) -> None:
        self.timeout = default_timeout
        self.total_timeout = total_timeout
        self.msg: Message = None
        self._initialized = False

    async def initialize(self):
        pass

    @property
    @abstractmethod
    def username(self):
        pass

    async def start_bot(self, **kwargs):
        if not self._initialized:
            await self.initialize()
        await self.send_command("start", **kwargs)

    async def reactivate_bot(self):
        """ Override if the bot has unusual behavior """
        await self.start_bot()

    def _args(self, kwargs: Dict = None) -> Dict:
        default = dict(
            entity=self.username, timeout=self.timeout, total_timeout=self.total_timeout
        )
        if kwargs:
            return {
                **default,
                **kwargs,
            }  # TODO: make sure this overrides the default dict and not vice versa
        return default

    async def send_message(self, text: str, **conversation_kwargs):
        return await self._communicate(lambda conv: conv.send_message(text), **conversation_kwargs)

    async def send_file(self, file: Any, caption: str = None, **conversation_kwargs):
        return await self._communicate(
            lambda conv: conv.send_file(file, caption=caption), **conversation_kwargs
        )

    async def send_command(self, name: str, **kwargs):
        return await self._communicate(
            lambda conv: conv.send_message(f"/{name.lstrip('/')}"), **kwargs
        )

    async def click_button(self, query: str, matcher: Matcher = Matcher.Equals):
        result = await self.msg.click(filter=lambda b: matcher.match(b.text, query))
        if result is None:
            return
        if isinstance(result, BotCallbackAnswer):
            return result
        print(result.stringify())
        raise NotImplementedError("TODO: implement non-BotCallbackAnswer responses")

    async def send_inline_query(self, query: str) -> InlineResults:
        return await self.client.inline_query(self.username, query)

    async def _communicate(self, func: Callable[[Conversation], Any], **kwargs) -> Message:
        """
        Sends user_message and fetches a response
        TODO: fetch multiple responses like in tgintegration
        """
        async with self.client.conversation(**self._args(kwargs)) as conv:
            print("executing")
            sent = await func(conv)
            print("done,", sent)
            response = await conv.get_response(sent)
            assert isinstance(response, Message)
            self.msg = response
            return self.msg

        # args = self._args(kwargs)
        # responses = []
        #
        # async with self.use.conversation(self._args(kwargs)) as conv:
        #     sent = await func()
        #     return await conv.get_response(sent)
        #
        # async with self.use.conversation(args) as conv:
        #     wait_event = conv.wait_event(NewMessage(incoming=True))
        #     sent = await func()
        #     return await conv.get_response(sent)
        #
        # user_message = await self.conversation.send_message(*args, **kwargs)
        # if expected > 1:
        #     result = [await self.conversation.get_response(user_message) for _ in range(expected)]
        # else:
        #     result = await self.conversation.get_response(user_message)
        #
        # if sleep:
        #     await asyncio.sleep(sleep)
        #
        # return result


# region utils
def is_media_event(event: NewMessage) -> bool:
    return bool(event.message_descriptor.media)


# endregion
