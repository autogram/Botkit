from pyrogram import Message

from botkit.routing.pipelines.callbacks import HandlerSignature
from botkit.routing.pipelines.factories.base import UpdatePipelineFactory
from botkit.routing.pipelines.factories.steps.custom_handler_step_factory import (
    CustomHandlerStepFactory,
)
from botkit.routing.pipelines.factories.steps.delete_trigger_step_factory import (
    DeleteTriggerStepFactory,
)
from botkit.routing.pipelines.factories.steps.gather_step_factory import GatherStepFactory
from botkit.routing.pipelines.factories.steps.view_render_step_factory import ViewRenderStepFactory
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient
from botkit.views.botkit_context import BotkitContext


class MessagePipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.message

    def create_callback(self) -> HandlerSignature:
        assert (
            self.plan._reducer is None
        ), "Reducer was specified but that is an undefined state for a message handler."

        gather_initial_state, gather_async = GatherStepFactory.create_step(self.plan._gatherer)
        send_view = ViewRenderStepFactory.create_step(self.plan._view)
        handle, handle_async = CustomHandlerStepFactory.create_step(self.plan._handler)
        should_transition = self.plan._state_transition
        delete_trigger = DeleteTriggerStepFactory.create_step(self.plan._should_delete_trigger)

        async def handle_message(client: IClient, message: Message) -> None:
            context = BotkitContext(client=client, update=message, state=None)

            if gather_initial_state is not None:
                if gather_async:
                    context.state = await gather_initial_state(context)
                else:
                    context.state = gather_initial_state(context)

            if send_view:
                await send_view(context)

            if handle:
                if handle_async:
                    return await handle(message, context)
                else:
                    return handle(message, context)

            if delete_trigger is not None:
                await delete_trigger(context)

        return handle_message

    def get_description(self) -> str:
        pass
