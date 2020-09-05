import asyncio
from dataclasses import dataclass
from logging import Handler, LogRecord, NOTSET
from typing import Union

from haps import Inject, Config

from botkit.libraries.annotations import IClient


@dataclass
class ChannelLogConfig:
    log_chat: Union[int, str] = Config("LOG_CHAT")
    level: int = NOTSET


class ChatLogHandler(Handler):
    def __init__(self, client: IClient, config: ChannelLogConfig):
        raise NotImplemented()
        self.client = client
        self.peer_channel = self._lookup.resolve_peer(config.log_chat)
        super(ChatLogHandler, self).__init__(config.level)

    def emit(self, record: LogRecord):
        text = self.format(record)
        asyncio.run_coroutine_threadsafe(
            self.client.send_message(self.peer_channel, text), self.client.ping_loop
        )
