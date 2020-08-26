from typing import Any, Union

from pyrogram.types import CallbackQuery

from botkit.libraries.annotations import HandlerSignature
from botkit.routing.pipelines.factories.updates.update_pipeline_factory import (
    UpdatePipelineFactory,
)
from botkit.routing.pipelines.factories.steps.custom_handler_step_factory import (
    CustomHandlerStepFactory,
)
from botkit.routing.pipelines.factories.steps.gather_step_factory import GatherStepFactory
from botkit.routing.pipelines.factories.steps.reduce_step_factory import ReduceStepFactory
from botkit.routing.pipelines.factories.steps.render_view_step_factory import RenderViewStepFactory
from botkit.routing.pipelines.factories.steps.send_view_step_factory import (
    CommitRenderedViewStepFactory,
)
from botkit.routing.types import TState
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient
from botkit.views.botkit_context import BotkitContext


class CallbackQueryPipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self):
        return UpdateType.callback_query

    # TODO: implement
    # def create_update_filter(self) -> UpdateFilterSignature:
    #     pass  # TODO: not game

    def create_callback(self) -> HandlerSignature:
        gather_initial_state, gather_async = GatherStepFactory.create_step(self.plan._gatherer)
        mutate_previous_state, mutate_async = ReduceStepFactory.create_step(self.plan._reducer)
        render_view = RenderViewStepFactory.create_step(self.plan._view)
        commit_rendered_view = CommitRenderedViewStepFactory.create_step(self.plan._view)
        handle, handle_async = CustomHandlerStepFactory.create_step(self.plan._handler)

        async def handle_callback_query(
            client: IClient, callback_query: CallbackQuery, context: BotkitContext = None
        ) -> Union[bool, Any]:

            if not context:
                raise NotImplementedError("No context provided for callback query.")

            next_state = None
            if gather_initial_state:
                if gather_async:
                    next_state: Any = await gather_initial_state()
                else:
                    next_state: Any = gather_initial_state()
            elif mutate_previous_state:
                if mutate_async:
                    next_state: TState = await mutate_previous_state(context.state, context)
                else:
                    next_state: TState = mutate_previous_state(context.state, context)

            if next_state:
                context.state = next_state

            if render_view:
                # TODO: It remains to be seen whether having `rendered_message` on the `context` is useful.
                # It might turn out that just passing it to the `send_or_update` step is the better choice.
                context.rendered_message = render_view(context)
                await commit_rendered_view(context)

            if handle:
                if handle_async:
                    return await handle(callback_query, context)
                else:
                    return handle(callback_query, context)

        return handle_callback_query
