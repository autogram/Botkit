from pyrogram.types import Message

from botkit.libraries.annotations import HandlerSignature
from botkit.routing.pipelines.steps._base import Continue, StepError
from botkit.routing.pipelines.updates.update_pipeline_factory import (
    UpdatePipelineFactory,
)
from botkit.routing.pipelines.steps.custom_handler_step_factory import (
    CustomHandlerStepFactory,
)
from botkit.routing.pipelines.steps.delete_trigger_step_factory import (
    RemoveTriggerStepFactory,
)
from botkit.routing.pipelines.steps.gather_step_factory import (
    GatherStepError,
    GatherStepFactory,
)
from botkit.routing.pipelines.steps.render_view_step_factory import (
    RenderViewStepFactory,
)
from botkit.routing.pipelines.steps.commit_rendered_view_step_factory import (
    CommitRenderedViewStepFactory,
)
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient
from botkit.views.botkit_context import Context


class MessagePipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.message

    def create_unified_callback(self) -> HandlerSignature:
        assert (
            self.plan._reducer is None
        ), "Reducer was specified but that is an undefined state for a message handler."

        gather_initial_state, gather_async = GatherStepFactory.create_step(
            self.plan._gatherer
        )
        render_view = RenderViewStepFactory.create_step(self.plan._view)
        commit_rendered_view = CommitRenderedViewStepFactory.create_step(
            self.plan._view
        )
        handle, handle_async = CustomHandlerStepFactory.create_step(self.plan._handler)

        # TODO: state transitions
        # should_transition = self.plan._state_transition

        delete_trigger_message_async = RemoveTriggerStepFactory.create_step(
            self.plan._remove_trigger_setting
        )

        async def handle_message(client: IClient, message: Message) -> None:
            context = Context(client=client, update=message, state=None)

            try:
                if gather_initial_state is not None:
                    if gather_async:
                        context.state = await gather_initial_state(context)
                    else:
                        context.state = gather_initial_state(context)

                if render_view:
                    # TODO: It remains to be seen whether having `rendered_message` on the `context` is useful.
                    # It might turn out that just passing it to the `send_or_update` step is the better choice.
                    context.rendered_message = render_view(context)
                    await commit_rendered_view(context)

                if handle:
                    if handle_async:
                        return await handle(message, context)
                    else:
                        return handle(message, context)

            except StepError as e:
                if e.should_ignore_and_continue:
                    return
                raise e

            if delete_trigger_message_async is not None:
                await delete_trigger_message_async(context)

        return handle_message

    def get_description(self) -> str:
        pass
