import inspect
import warnings
from timeit import timeit
from typing import Any, Awaitable, Callable, List, Optional, Union, cast

from pyrogram import Update
from pyrogram.errors import MessageIdInvalid

from botkit.routing.pipelines.execution_plan import SendTarget, SendTo, ViewParameters
from botkit.routing.pipelines.factories.factory_types import IStepFactory
from botkit.routing.update_types.updatetype import UpdateType
from botkit.services.companionbotservice import CompanionBotService
from botkit.views.base import RenderedMessageBase
from botkit.views.botkit_context import BotkitContext
from botkit.views.functional_views import quacks_like_view_render_func, render_functional_view
from botkit.views.views import MessageViewBase


class RenderViewStepFactory(
    IStepFactory[ViewParameters, Optional[Callable[[BotkitContext], RenderedMessageBase]]]
):
    @property
    def applicable_update_types(self) -> List[UpdateType]:
        return [UpdateType.message, UpdateType.callback_query, UpdateType.poll]

    # TODO: something breaks PyCharm's type inference here...
    @classmethod
    def create_step(cls, view_params: ViewParameters):
        if view_params is None:
            return None

        is_view_render_func = quacks_like_view_render_func(view_params.view)
        create_view_instance_dynamically = inspect.isclass(view_params.view)

        def render_view(context: BotkitContext) -> RenderedMessageBase:
            if is_view_render_func:
                return render_functional_view(view_params.view, context.state)

            elif create_view_instance_dynamically:
                view_instance = view_params.view(context.state)

                if context.state is None:
                    # First try to instantiate the view, then warn if that succeeded without an exception despite
                    # a `None`-state.
                    warnings.warn(
                        f"`None` state is being passed to view {view_params.view}. Check your state generation "
                        f"and/or mutations."
                    )

                return view_instance.render()

            else:
                return cast(MessageViewBase, view_params.view).render()

        return render_view
