import asyncio
import traceback
from dataclasses import dataclass
from logging import Handler, LogRecord
from typing import Tuple, Union

from botkit.builders import ViewBuilder
from botkit.core.components import Component
from botkit.agnostic.annotations import IClient
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.settings import botkit_settings
from botkit.views.botkit_context import Context
from botkit.views.functional_views import ViewRenderFuncSignature, render_functional_view


class ChatLoggerComponent(Component):
    def register(self, routes: RouteBuilder):
        pass

    async def invoke(self, context: Context):
        pass


@dataclass
class ChatLoggerConfig:
    client: IClient
    log_chat: Union[int, str]
    level_name: Union[int, str] = "WARNING"


def _default_renderer(props: Tuple[str, LogRecord], builder: ViewBuilder):
    text, record = props
    builder.html.code(record.filename)

    if record.funcName:
        builder.html.spc().text("(").code(record.funcName).text(")")

    builder.html.text(":").br().text(record.message)


def _filter_by_current_level(record):
    return record["level"].no >= botkit_settings.log_level


async def emit_log():
    pass


class ChatLogHandler(Handler):
    def __init__(
        self,
        client: IClient,
        config: ChatLoggerConfig,
        render_log_entry: ViewRenderFuncSignature = _default_renderer,
    ):
        self.render_log_entry = render_log_entry
        self.client = client
        self.log_chat = config.log_chat

        super(ChatLogHandler, self).__init__(config.level)

    def handle(self, record: LogRecord) -> None:
        super().handle(record)

    def emit(self, record: LogRecord):
        text = self.format(record)
        asyncio.run_coroutine_threadsafe(
            self._render_and_send((text, record)), asyncio.get_event_loop()
        )

    async def _render_and_send(self, text_and_record: Tuple[str, LogRecord]):
        rendered = render_functional_view(self.render_log_entry, text_and_record)
        try:
            await self.client.send_rendered_message(self.log_chat, rendered)
        except:
            traceback.print_exc()
