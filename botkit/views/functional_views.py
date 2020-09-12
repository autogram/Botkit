import inspect
from typing import (
    Any,
    Callable,
    Optional,
    TypeVar,
)

from decorators import FuncDecorator

from botkit.builders import ViewBuilder
from botkit.views.rendered_messages import RenderedMessage

T = TypeVar("T")


def quacks_like_view_render_func(obj: Any) -> bool:
    if inspect.isclass(obj):
        return False
    if not callable(obj):
        return False
    if len(inspect.signature(obj).parameters) < 2:
        return False
    return True


def render_functional_view(view_func: Callable, state: Optional[Any]) -> RenderedMessage:
    # TODO: Decide if htis is a good idea
    # if view_state is None:
    #     raise ValueError("No view_state was specified, cannot render.")

    # # TODO: (see paraminjector/TODO.md)
    # # TODO: Handle reply keyboards
    # # TODO: add a MediaBuilder
    # # TODO: allow only certain combinations of parameters
    # call_with_args(
    #     view_func, {type(builder): builder, type(menu): menu, type(meta): meta,},
    # )

    builder = ViewBuilder(state)
    view_func(state, builder)

    return builder.render()


TViewState = TypeVar("TViewState", bound=type)

# X = TypeVar("X", contravariant=True)
# class ViewFuncSignature(Protocol[X]):
# @overload
# def __call__(self, view_state: X, builder: HtmlBuilder):
#     pass
#
# @overload
# def __call__(self, view_state: X, builder: HtmlBuilder, menu: InlineMenuBuilder):
#     pass
#
# @overload
# def __call__(self, view_state: X, menu: InlineMenuBuilder):
#     pass
#
# @overload
# def __call__(self, view_state: X, builder: HtmlBuilder, markup: ReplyMarkupBuilder):
#     pass
#
# def __call__(self, *args, **kwargs):
#     pass


ViewRenderFuncSignature = Callable[[TViewState, ViewBuilder], Optional[Any]]


class _ViewDecorator(FuncDecorator):
    def decorate_func(self, *args, **kwargs):
        return super().decorate_func(*args, **kwargs)


view = _ViewDecorator
