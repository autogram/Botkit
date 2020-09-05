import asyncio
import logging
from dataclasses import dataclass
from logging import Handler, StreamHandler, LogRecord, NOTSET
from typing import Tuple, Union

from decouple import config
from haps import Inject
from haps.config import Config

from botkit.builders import ViewBuilder
from botkit.libraries.annotations import IClient
from botkit.views.functional_views import ViewRenderFuncSignature, render_functional_view
import logzero


@dataclass
class ChannelLogConfig:
    client: IClient
    log_chat: Union[int, str]
    level: int = NOTSET


def default_renderer(props: Tuple[str, LogRecord], builder: ViewBuilder):
    text, record = props
    builder.html.text(text)


class ChatLogHandler(Handler):
    def __init__(
        self,
        client: IClient,
        config: ChannelLogConfig,
        render_log_entry: ViewRenderFuncSignature = default_renderer,
    ):
        self.render_log_entry = render_log_entry
        self.client = client
        self.log_chat = config.log_chat

        super(ChatLogHandler, self).__init__(config.level)

    def handle(self, record: LogRecord) -> None:
        print("handle called")
        super().handle(record)

    def emit(self, record: LogRecord):
        text = self.format(record)
        asyncio.run_coroutine_threadsafe(
            self._render_and_send((text, record)), asyncio.get_event_loop()
        )

    async def _render_and_send(self, text_and_record: Tuple[str, LogRecord]):
        rendered = render_functional_view(self.render_log_entry, text_and_record)
        print(self.log_chat)
        await self.client.send_rendered_message(self.log_chat, rendered)
