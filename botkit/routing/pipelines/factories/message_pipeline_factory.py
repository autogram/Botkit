from pyrogram import Message

from botkit.routing.pipelines.callbacks import CallbackSignature
from botkit.routing.pipelines.factories.base import PipelineFactory
from botkit.routing.pipelines.gatherer import GatherStepFactory
from botkit.routing.pipelines.view_render_step_factory import ViewRenderStepFactory
from botkit.views.botkit_context import BotkitContext
from botkit.views.sender_interface import IViewSender


class MessagePipelineFactory(PipelineFactory):
    def create_callback(self) -> CallbackSignature:
        assert (
            self.plan._reducer is None
        ), "Reducer was specified but that is an undefined state for a message handler."

        gather_initial_state, gather_async = GatherStepFactory.create_step(self.plan._gatherer)
        send_view = ViewRenderStepFactory.create_step(self.plan._view)
        handler = self.plan._handler
        should_transition = self.plan._state_transition

        async def handle_message(client: IViewSender, message: Message) -> None:
            context = BotkitContext(client=client, update=message, state=None)

            if gather_initial_state is not None:
                context.state = await gather_initial_state(context)

            if send_view:
                await send_view(context)

            if handler:
                await handler.func(client, message)

        return handle_message

    def get_description(self) -> str:
        pass
