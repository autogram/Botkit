from functools import wraps
from typing import Any, Union

from pyrogram import CallbackQuery

from botkit.dispatching.callbackqueries.callback_manager import CallbackActionContext
from botkit.routing.pipelines.callbacks import CallbackSignature
from botkit.routing.pipelines.factories.base import PipelineFactory
from botkit.routing.pipelines.gatherer import GatherStepFactory
from botkit.routing.pipelines.reduce_step_factory import ReduceStepFactory
from botkit.routing.pipelines.view_render_step_factory import ViewRenderStepFactory
from botkit.routing.types import TState
from botkit.views.botkit_context import BotkitContext
from botkit.views.renderer_client_mixin import PyroRendererClientMixin


class CallbackQueryPipelineFactory(PipelineFactory):
    # def create_update_filter(self) -> UpdateFilterSignature:
    #     pass  # TODO: not game

    def create_callback(self) -> CallbackSignature:
        gather_initial_state, gather_async = GatherStepFactory.create_step(self.plan._gatherer)
        mutate_previous_state, mutate_async = ReduceStepFactory.create_step(self.plan._reducer)
        send_view = ViewRenderStepFactory.create_step(self.plan._view)
        handler = self.plan._handler

        async def handle_callback_query(
            client: PyroRendererClientMixin, callback_query: CallbackQuery, context: BotkitContext = None
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

            if send_view:
                await send_view(context)

            if handler:
                return await handler.func(client, callback_query, next_state)

        if handler:
            wraps(handle_callback_query, handler.func)
        return handle_callback_query
