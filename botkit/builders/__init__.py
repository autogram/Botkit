from typing import Any

from .htmlbuilder import HtmlBuilder
from .inlinemenubuilder import InlineMenuBuilder
from .metabuilder import MetaBuilder
from ..views.rendered_messages import RenderedMessage, RenderedTextMessage


class ViewBuilder:
    html: HtmlBuilder
    menu: InlineMenuBuilder
    meta: MetaBuilder

    def __init__(self, state: Any):
        self.html = HtmlBuilder()
        self.menu = InlineMenuBuilder(state)
        self.meta = MetaBuilder()

    def render(self) -> RenderedMessage:
        # TODO: implement the other message types
        return RenderedTextMessage(
            text=self.html.render(),
            inline_buttons=self.menu.render(),
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
