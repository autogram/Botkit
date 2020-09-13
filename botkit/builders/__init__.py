from typing import Any

from haps import Container

from .htmlbuilder import HtmlBuilder
from .menubuilder import MenuBuilder
from .metabuilder import MetaBuilder
from ..persistence.callback_store import CallbackStoreBase
from ..settings import botkit_settings
from ..views.rendered_messages import RenderedMessage, RenderedTextMessage


class ViewBuilder:
    html: HtmlBuilder
    menu: MenuBuilder
    meta: MetaBuilder

    def __init__(self, state: Any, callback_manager: CallbackStoreBase = None):
        if callback_manager is None:
            callback_manager = Container().get_object(
                CallbackStoreBase, botkit_settings.callback_manager_qualifier
            )
        self.html = HtmlBuilder(state)
        self.menu = MenuBuilder(state, callback_manager)
        self.meta = MetaBuilder()

    @property
    def is_dirty(self) -> bool:
        return any((x.is_dirty for x in [self.html, self.menu, self.meta]))

    def render(self) -> RenderedMessage:
        # TODO: implement the other message types aswell
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
