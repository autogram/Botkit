import inspect
from loguru import logger as log
from typing import (
    Any,
    Callable,
    Optional,
    TypeVar,
)

from decorators import FuncDecorator

from botkit.builders import CallbackBuilder, HtmlBuilder, MenuBuilder, MetaBuilder, ViewBuilder
from botkit.persistence.callback_store import ICallbackStore
from botkit.views.rendered_messages import RenderedMessage
from paraminjector import call_with_args

T = TypeVar("T")


def quacks_like_view_render_func(obj: Any) -> bool:
    if inspect.isclass(obj):
        return False
    if not callable(obj):
        return False
    if len(inspect.signature(obj).parameters) < 2:
        return False
    return True


_RenderedMessageType = TypeVar("_RenderedMessageType", bound=RenderedMessage, covariant=True)


def render_functional_view(
    view_func: Callable, state: Optional[Any], callback_store: ICallbackStore = None
) -> _RenderedMessageType:
    builder = ViewBuilder(CallbackBuilder(state=state, callback_store=callback_store))

    try:
        # TODO: use the static version of paraminjector
        # TODO: allow only certain combinations of parameters as feature of paraminjector
        call_with_args(
            view_func,
            available_args={
                ViewBuilder: builder,
                HtmlBuilder: builder.html,
                MenuBuilder: builder.menu,
                MetaBuilder: builder.meta,
            },
            fixed_pos_args=(state,),
        )
    except Exception as e:
        try:
            view_func(state, builder)
        except:
            log.exception(str(e), e)

    return builder.render()


TViewState = TypeVar("TViewState", bound=type)


ViewRenderFuncSignature = Callable[[TViewState, ViewBuilder], Optional[Any]]


class _ViewDecorator(FuncDecorator):
    def decorate_func(self, *args, **kwargs):
        return super().decorate_func(*args, **kwargs)


view = _ViewDecorator
