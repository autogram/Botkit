import inspect
import warnings
from typing import Callable, List, Optional, cast

from botkit.routing.pipelines.execution_plan import ViewParameters
from botkit.routing.pipelines.factory_types import IStepFactory
from botkit.routing.pipelines.steps._base import StepError
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context
from botkit.views.functional_views import (
    quacks_like_view_render_func,
    render_functional_view,
)
from botkit.views.rendered_messages import RenderedMessageBase
from botkit.views.views import MessageViewBase


class RenderViewStepError(StepError):
    pass


class RenderViewStepFactory(
    IStepFactory[ViewParameters, Optional[Callable[[Context], RenderedMessageBase]]]
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
        view_renderer_name = (
            view_params.view.__name__
            if hasattr(view_params.view, "__name__")
            else str(view_params.view)
        )

        log = create_logger("renderer")

        def render_view(context: Context) -> RenderedMessageBase:
            log.debug(f"Rendering view using {view_renderer_name}")

            try:
                if is_view_render_func:
                    return render_functional_view(view_params.view, context.view_state)

                elif create_view_instance_dynamically:
                    view_instance = view_params.view(context.view_state)

                    if context.view_state is None:
                        # First try to instantiate the view, then warn if that succeeded without an exception despite
                        # a `None`-view_state.
                        warnings.warn(
                            f"`None` state is being passed to view {view_params.view}. Check your state generation "
                            f"and/or mutations."
                        )

                    return view_instance.render()

                else:
                    return cast(MessageViewBase, view_params.view).render()
            except Exception as e:
                raise RenderViewStepError(e)

        return render_view
