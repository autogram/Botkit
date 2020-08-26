from dataclasses import dataclass
from typing import Any, List, Literal, Optional, Union

from pyrogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from botkit.views.types import KeyboardTypes


class RenderedMessageBase:
    pass


@dataclass
class RenderedMessageMarkup(RenderedMessageBase):
    reply_markup: Union[ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove] = None
    inline_buttons: Optional[List[List[KeyboardTypes]]] = None

    @property
    def inline_keyboard_markup(self) -> Optional[InlineKeyboardMarkup]:
        if self.inline_buttons is None:
            return None
        rows = [list(x) for x in self.inline_buttons]
        return InlineKeyboardMarkup(rows)


@dataclass
class RenderedMessage(RenderedMessageMarkup):
    title: Optional[str] = None
    description: Optional[str] = None

    parse_mode: str = "html"
    disable_web_page_preview: bool = True

    thumb_url: str = None  # TODO: implement


@dataclass
class RenderedStickerMessage(RenderedMessage):
    sticker: Optional[str] = None


@dataclass
class RenderedMediaMessage(RenderedMessage):
    media: Optional[Any] = None
    caption: Optional[str] = None


@dataclass
class RenderedTextMessage(RenderedMessage):
    text: Optional[str] = None


@dataclass
class RenderedPollMessage(RenderedMessageMarkup):
    question: str = None
    options: List[str] = None
    is_anonymous: bool = True
    allows_multiple_answers: bool = None
    type: Literal["regular", "quiz"] = None
    correct_option_id: int = None
