import inspect
from typing import Any, Union

from haps import Container

from botkit.agnostic import HandlerSignature
from botkit.persistence.data_store import DataStoreBase
from botkit.routing.pipelines.executionplan import ExecutionPlan
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
from botkit.routing.triggers import RouteTriggers
from tgtypes.updatetype import UpdateType
from botkit.clients.client import IClient
from botkit.utils.botkit_logging.setup import create_logger
from botkit.botkit_context import Context


class UpdatePipelineFactory:
    def __init__(self, data_store: DataStoreBase = None):
        self.data_store: DataStoreBase = data_store or Container().get_object(DataStoreBase)

    def build_callback(self, plan: ExecutionPlan, for_update_type: UpdateType) -> HandlerSignature:
        # TODO: Main goals with the generalized pipeline steps should be:
        # - Performance (by preprocessing anything that's known at startup time)
        # - Allow users to override existing and inject their own steps

        initialize_context_async = InitializeContextStep(
            for_update_type, data_store=self.data_store
        )
        gather_initial_state, gather_async = GatherStepFactory.create_step(plan._gatherer)
        mutate_previous_state, mutate_async = ReduceStepFactory.create_step(plan._reducer)
        invoke_component = InvokeComponentStepFactory.create_step(plan._handling_component)
        render_view = RenderViewStepFactory.create_step(plan._view)
        commit_rendered_view_async = CommitRenderedViewStepFactory.create_step(plan._view)
        handle, handle_async = CallStepFactory.create_step(plan._handler)
        _rm_trigger_params = plan._remove_trigger_params
        always_remove_trigger = _rm_trigger_params and _rm_trigger_params.always
        remove_trigger_early = _rm_trigger_params and _rm_trigger_params.early
        delete_trigger_message_async = RemoveTriggerStepFactory.create_step(_rm_trigger_params)
        postprocess_data, postprocess_data_async = CollectStepFactory.create_step(plan._collector)

        send_from = plan._view.send_from if plan._view else None

        # TODO: view_state transitions
        # should_transition = plan._state_transition

        log = create_logger("pipeline")

        async def handle_update(
            client: IClient, update: Any, context: Context = None
        ) -> Union[bool, Any]:
            context = await initialize_context_async(client, update, context)
            handle_result: Any = None

            if always_remove_trigger and remove_trigger_early:
                await delete_trigger_message_async(context)

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
                    if send_from:
                        # TODO: Kinda hacky, but otherwise `evaluate_send_target` doesn't have the right callback
                        #  context...
                        # - Make sure that there are no @cached_properties on the context if this remains!
                        context.client = send_from

                    # TODO: It remains to be seen whether having `rendered_message` on the `context` is useful.
                    # It might turn out that just passing it to the `send_or_update` step is the better choice.
                    context.rendered_message = render_view(context)

                    try:
                        await commit_rendered_view_async(context)
                    except:
                        log.exception("commit_rendered_view_async")

                    if send_from:
                        # Reset
                        context.client = client

                if handle:
                    if handle_async:
                        handle_result = await handle(update, context)
                    else:
                        handle_result = handle(update, context)

                    # render_view = RenderViewStepFactory.create_step(plan._view)
                    # commit_rendered_view = CommitRenderedViewStepFactory.create_step(plan._view)

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
                            " because " + reason[0].lower() + reason[1:]
                            if (reason := e.inner_exception.reason)
                            else ""
                        )
                    )
                    return
                raise e
            finally:
                if always_remove_trigger and not remove_trigger_early:
                    await delete_trigger_message_async(context)

            if not always_remove_trigger and delete_trigger_message_async is not None:
                await delete_trigger_message_async(context)

            await self.data_store.synchronize_context_data(context)

            return handle_result

        return handle_update

    def get_description(
        self, triggers: RouteTriggers, plan: ExecutionPlan, for_update_type: UpdateType
    ) -> str:
        parts = []
        if triggers.action is not None:
            parts.append("ActionHandler(")

            if plan._handler:
                parts.append(plan._handler.name)
            elif view := plan._view:

                # TODO: nice string from the view parameters
                parts.append(view.command.title())
                parts.append(" ")
                parts.append(
                    view.view.__class__.__name__
                    if inspect.isclass(view.view)
                    else view.view.__name__
                )
                parts.append(str(view.send_target))

            if plan._reducer:
                reducer_name = plan._reducer.name
                if "lambda" not in reducer_name:
                    parts.append(f", reducer={reducer_name}")

            if plan._gatherer:
                gatherer_name = plan._gatherer.name
                if "lambda" not in gatherer_name:
                    parts.append(f", reducer={gatherer_name}")
        else:
            pipeline_name = self.__class__.__name__.replace("Factory", "")

            parts.append(f"{pipeline_name}(")
            if plan._handler:
                parts.append(plan._handler.name)
            else:
                args = []
                if plan._gatherer:
                    args.append(f"gatherer={plan._gatherer}")
                if plan._reducer:
                    args.append(f"reducer={plan._reducer}")
                if plan._view:
                    args.append(f"view={plan._view.view}")
                parts.append(", ".join(args))

        if triggers.filters is not None:
            parts.append(", filters=")
            parts.append(type(triggers.filters).__name__)

        parts.append(")")
        return "".join(parts)

    def create_update_filter(self, triggers: RouteTriggers) -> UpdateFilterSignature:
        return triggers.filters
        # cond = triggers.condition
        # filters = triggers.filters
        #
        # cond_is_awaitable = cond and inspect.isawaitable(cond)
        #
        # async def check(client: IClient, update: Update) -> bool:
        #     if cond is not None:
        #
        #         if cond_is_awaitable:
        #             if not await cond():
        #                 return False
        #
        #     if filters:
        #         try:
        #             return await filters(client, update)
        #         except:
        #             print(filters)
        #             print(type(filters))
        #             traceback.print_exc()
        #
        #     return False
        #
        # # TODO: Hotfix for weird PR in pyro
        # check.__call__ = check
        #
        # return check
