from paraminjector import call_with_args
from typing import (
    Any,
    Callable,
    TypeVar,
    overload,
)
from typing_extensions import Protocol

from botkit.builders.htmlbuilder import HtmlBuilder
from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from botkit.builders.metabuilder import MetaBuilder
from botkit.builders.replymarkupbuilder import ReplyMarkupBuilder
from botkit.views.base import RenderedMessage

T = TypeVar("T")


def render_functional_view(view_func: Callable, state: Any) -> RenderedMessage:
    if state is None:
        raise ValueError("No choices was specified, cannot render.")

    builder = HtmlBuilder()
    menu = InlineMenuBuilder(state)
    meta = MetaBuilder()

    # TODO: (see paraminjector/TODO.md)
    # TODO: Handle reply keyboards
    # TODO: add a MediaBuilder
    # TODO: allow only certain combinations of parameters
    call_with_args(
        view_func, {type(builder): builder, type(menu): menu, type(meta): meta,},
    )

    rendered = RenderedMessage(
        text=builder.render(), inline_buttons=menu.render(), title=meta.title, description=meta.description,
    )

    return rendered


TModel = TypeVar("TModel", bound=type)

X = TypeVar("X", contravariant=True)


class ViewFuncSignature(Protocol[X]):
    @overload
    def __call__(self, state: X, builder: HtmlBuilder):
        pass

    @overload
    def __call__(self, state: X, builder: HtmlBuilder, menu: InlineMenuBuilder):
        pass

    @overload
    def __call__(self, state: X, menu: InlineMenuBuilder):
        pass

    @overload
    def __call__(self, state: X, builder: HtmlBuilder, markup: ReplyMarkupBuilder):
        pass

    def __call__(self, *args, **kwargs):
        pass


def view(state: TModel) -> Callable[[ViewFuncSignature[TModel]], ViewFuncSignature[TModel]]:
    def wrap(func: ViewFuncSignature):
        return func

    return wrap
