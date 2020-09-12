import inspect
from typing import Any, Optional, Union

from botkit.libraries import HandlerSignature
from botkit.routing.pipelines.execution_plan import ExecutionPlan
from botkit.routing.pipelines.filters import UpdateFilterSignature
from botkit.routing.pipelines.steps._base import Continue, StepError
from botkit.routing.pipelines.steps.call_step_factory import CallStepFactory
from botkit.routing.pipelines.steps.collect_step_factory import CollectStepFactory
from botkit.routing.pipelines.steps.commit_rendered_view_step_factory import (
    CommitRenderedViewStepFactory,
)
from botkit.routing.pipelines.steps.gather_step_factory import GatherStepFactory
from botkit.routing.pipelines.steps.initialize_context_step import InitializeContextStep
from botkit.routing.pipelines.steps.invoke_component_step_factory import InvokeComponentStepFactory
from botkit.routing.pipelines.steps.reduce_step_factory import ReduceStepFactory
from botkit.routing.pipelines.steps.remove_trigger_step_factory import RemoveTriggerStepFactory
from botkit.routing.pipelines.steps.render_view_step_factory import RenderViewStepFactory
from botkit.routing.pipelines.steps.synchronize_context_step import SynchronizeContextStep
from botkit.routing.triggers import RouteTriggers
from botkit.routing.types import TViewState
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context


class UpdatePipelineFactory:
    synchronize_context_step = SynchronizeContextStep()

    def __init__(self, triggers: RouteTriggers, plan: ExecutionPlan, for_update_type: UpdateType):
        self.initialize_context_step = InitializeContextStep(for_update_type)
        self.triggers = triggers
        self.plan = plan
        self.update_type = for_update_type

    def build_callback(self) -> HandlerSignature:
        # TODO: Main goals with the generalized pipeline steps should be:
        # - Performance
        # - Allow users to override existing and inject their own steps

        update_type = self.update_type
        initialize_context_async = self.initialize_context_step
        gather_initial_state, gather_async = GatherStepFactory.create_step(self.plan._gatherer)
        mutate_previous_state, mutate_async = ReduceStepFactory.create_step(self.plan._reducer)
        invoke_component = InvokeComponentStepFactory.create_step(self.plan._handling_component)
        render_view = RenderViewStepFactory.create_step(self.plan._view)
        commit_rendered_view_async = CommitRenderedViewStepFactory.create_step(self.plan._view)
        handle, handle_async = CallStepFactory.create_step(self.plan._handler)
        delete_trigger_message_async = RemoveTriggerStepFactory.create_step(
            self.plan._remove_trigger_setting
        )
        synchronize_context_async = self.synchronize_context_step
        postprocess_data, postprocess_data_async = CollectStepFactory.create_step(
            self.plan._collector
        )

        # TODO: view_state transitions
        # should_transition = self.plan._state_transition

        log = create_logger("pipeline")

        async def handle_update(
            client: IClient, update: Any, context: Context = None
        ) -> Union[bool, Any]:

            context = await initialize_context_async(client, update, context)

            try:
                if gather_initial_state:
                    if gather_async:
                        await gather_initial_state(context)
                    else:
                        gather_initial_state(context)

                if mutate_previous_state:
                    if mutate_async:
                        await mutate_previous_state(context.view_state, context)
                    else:
                        mutate_previous_state(context.view_state, context)

                if invoke_component:
                    await invoke_component(context)

                if render_view:
                    # TODO: It remains to be seen whether having `rendered_message` on the `context` is useful.
                    # It might turn out that just passing it to the `send_or_update` step is the better choice.
                    context.rendered_message = render_view(context)
                    await commit_rendered_view_async(context)

                if handle:
                    if handle_async:
                        handle_result = await handle(update, context)
                    else:
                        handle_result = handle(update, context)

                    # render_view = RenderViewStepFactory.create_step(self.plan._view)
                    # commit_rendered_view = CommitRenderedViewStepFactory.create_step(self.plan._view)

                if postprocess_data:
                    if postprocess_data_async:
                        await postprocess_data(context)
                    else:
                        postprocess_data(context)

            except StepError as e:
                if e.should_ignore_and_continue:
                    log.debug(
                        ("Continuing" if isinstance(e.inner_exception, Continue) else "Breaking")
                        + " execution"
                        + (
                            " because " + reason[0].lower() + reason[1:].upper()
                            if (reason := e.inner_exception.reason)
                            else ""
                        )
                    )
                    return
                raise e

            if delete_trigger_message_async is not None:
                await delete_trigger_message_async(context)

            await synchronize_context_async(context)

        return handle_update

    def get_description(self) -> str:
        parts = []
        if self.triggers.action is not None:
            parts += "ActionHandler("

            if self.plan._handler:
                parts += {self.plan._handler.name}
            elif (view := self.plan._view) :

                # TODO: nice string from the view parameters
                parts += view.command.title()
                parts += " "
                parts += (
                    view.view.__class__.__name__
                    if inspect.isclass(view.view)
                    else view.view.__name__
                )
                parts += str(view.send_target)

            if self.plan._reducer:
                reducer_name = self.plan._reducer.name
                if "lambda" not in reducer_name:
                    parts += f", reducer={reducer_name}"

            if self.plan._gatherer:
                gatherer_name = self.plan._gatherer.name
                if "lambda" not in gatherer_name:
                    parts += f", reducer={gatherer_name}"
        else:
            pipeline_name = self.__class__.__name__.replace("Factory", "")

            parts += f"{pipeline_name}("
            if self.plan._handler:
                parts += self.plan._handler.name
            else:
                args = []
                if self.plan._gatherer:
                    args += f"gatherer={self.plan._gatherer}"
                if self.plan._reducer:
                    args += f"reducer={self.plan._reducer}"
                if self.plan._view:
                    args += f"view={self.plan._view.view}"
                parts += ", ".join(args)

        if self.triggers.filters is not None:
            parts += ", filters="
            parts += type(self.triggers.filters).__name__

        parts += ")"
        return "".join(parts)

    def create_update_filter(self) -> UpdateFilterSignature:
        return self.triggers.filters
        cond = self.triggers.condition
        filters = self.triggers.filters

        cond_is_awaitable = cond and inspect.isawaitable(cond)

        async def check(client: IClient, update: Update) -> bool:
            if cond is not None:

                if cond_is_awaitable:
                    if not await cond():
                        return False

            if filters:
                try:
                    return await filters(client, update)
                except:
                    print(filters)
                    print(type(filters))
                    traceback.print_exc()

            return False

        # TODO: Hotfix for weird PR in pyro
        check.__call__ = check

        return check
