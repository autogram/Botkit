from typing import Any, TYPE_CHECKING

from haps import Container, inject

from .callbackbuilder import CallbackBuilder

if TYPE_CHECKING:
    from botkit.widgets import Widget

from .htmlbuilder import HtmlBuilder
from .menubuilder import MenuBuilder
from .metabuilder import MetaBuilder
from ..persistence.callback_store import ICallbackStore
from ..settings import botkit_settings
from ..views.rendered_messages import RenderedMessage, RenderedTextMessage


class ViewBuilder:
    html: HtmlBuilder
    menu: MenuBuilder
    meta: MetaBuilder

    def __init__(self, callback_builder: CallbackBuilder):
        self.html = HtmlBuilder(callback_builder)
        self.menu = MenuBuilder(callback_builder)
        self.meta = MetaBuilder()

    def add(self, widget: "Widget"):
        self.html.add(widget)
        self.menu.add(widget)
        self.meta.add(widget)
        widget.render_html(self.html)

    @property
    def is_dirty(self) -> bool:
        return any((x.is_dirty for x in [self.html, self.menu, self.meta]))

    def render(self) -> RenderedMessage:
        # TODO: implement the other message types aswell
        html_text = self.html.render_html()
        rendered_menu = self.menu.render()
        return RenderedTextMessage(
            text=html_text,
            inline_buttons=rendered_menu,
            title=self.meta.title,
            description=self.meta.description,
        )


# def _determine_message_type(msg: RenderedMessageMarkup) -> MessageType:
#     if isinstance(msg, RenderedMessage):
#         if msg.media and msg.sticker:  # keep this check updated with new values!
#             raise ValueError("Ambiguous message type.")
#         if msg.sticker:
#             return MessageType.sticker
#         elif msg.media:
#             return MessageType.media
#         return MessageType.text
#     elif isinstance(msg, RenderedPollMessage):
#         return MessageType.poll
