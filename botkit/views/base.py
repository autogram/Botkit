from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from itertools import takewhile
from typing import (
    Any,
    Generic,
    List,
    Literal,
    Optional,
    TYPE_CHECKING,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from more_itertools import take
from pyrogram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from pyrogram.api.types import ReplyKeyboardMarkup

from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from botkit.builders.metabuilder import MetaBuilder

if TYPE_CHECKING:
    from botkit.routing.route_builder.builder import RouteBuilder as _RouteBuilder
else:
    _RouteBuilder = None


class IRegisterable(ABC):
    @classmethod
    def register(cls, routes: _RouteBuilder):
        pass


KeyboardTypes = Union[InlineKeyboardButton, Tuple]


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


TState = TypeVar("TState")


class ModelViewBase(Generic[TState], ABC):
    def __init__(self, state: TState):
        self.state = state


class InlineResultViewBase(ModelViewBase, IRegisterable, Generic[TState], ABC):
    def assemble_metadata(self, meta: MetaBuilder):
        pass

    def render(self) -> RenderedMessage:
        meta_builder = MetaBuilder()
        self.assemble_metadata(meta_builder)
        return RenderedMessage(title=meta_builder.title, description=meta_builder.description)


class RenderMarkupBase:  # not an interface as the methods need to exist
    @overload
    def render_markup(self, menu: InlineMenuBuilder):
        pass

    @overload
    def render_markup(self,) -> Union[ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove]:
        pass

    def render_markup(self, *args):
        pass
