from abc import ABC
from typing import (
    Generic,
    TYPE_CHECKING,
    Union,
    overload,
)

from pyrogram.types import ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove

from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from botkit.builders.metabuilder import MetaBuilder
from botkit.views.rendered_messages import RenderedMessage
from botkit.views.types import TViewState

if TYPE_CHECKING:
    from botkit.routing.route_builder.builder import RouteBuilder as _RouteBuilder
else:
    _RouteBuilder = None


class IRegisterable(ABC):
    @classmethod
    def register(cls, routes: _RouteBuilder):
        pass


class ModelViewBase(Generic[TViewState], ABC):
    def __init__(self, state: TViewState):
        self.state = state


class InlineResultViewBase(ModelViewBase, IRegisterable, Generic[TViewState], ABC):
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
