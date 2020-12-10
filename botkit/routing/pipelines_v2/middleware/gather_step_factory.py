from typing import Any, Coroutine, Set

from injector import Injector, inject
from unsync import Unfuture

from botkit.botkit_context import Context
from botkit.routing.pipelines.factory_types import ICallbackStepFactory, MaybeAsyncPipelineStep
from botkit.routing.pipelines.gatherer import (
    GathererSignature,
    GathererSignatureExamplesStr,
)
from botkit.routing.pipelines.steps._base import StepError
from botkit.routing.pipelines.steps.helpers.state_generators import update_view_state_if_applicable
from botkit.routing.pipelines_v2.base.middleware import (
    BaseMiddleware,
    AbstractGenericMiddleware,
    ConditionalMiddleware,
    EventType,
    NextDelegate,
)
from tgtypes.updatetype import UpdateType
from botkit.utils.botkit_logging.setup import create_logger
from botkit.utils.typed_callable import TypedCallable


class GatherStepError(StepError[GathererSignature]):
    pass


class GathererMiddleware(ConditionalMiddleware):
    @inject
    def __init__(self, injector: Injector):
        self.injector = injector

    @property
    def applicable_event_types(self) -> Set[EventType]:
        return {
            UpdateType.message,
            UpdateType.callback_query,
            UpdateType.inline_query,
            UpdateType.poll,
            UpdateType.user_status,
        }

    async def __call__(self, context: Context, call_next: NextDelegate[Context]) -> Any:
        self.injector.get()

    @classmethod
    def create_step(
        cls, gatherer: TypedCallable[GathererSignature]
    ) -> MaybeAsyncPipelineStep[GathererSignature]:
        if gatherer is None:
            return (None, None)

        if gatherer.num_non_optional_params == 0:
            requires_context = False
        elif gatherer.num_non_optional_params == 1:
            requires_context = True
        else:
            raise ValueError(
                f"Invalid number of arguments for gatherer {gatherer}. "
                f"Expected signature is: {GathererSignatureExamplesStr}"
            )

        log = create_logger("gatherer")

        is_coroutine = gatherer.is_coroutine

        if is_coroutine:

            async def gather_initial_state_async(context: Context):
                log.debug(f"Gathering initial state via {gatherer.name}")
                try:
                    if requires_context:
                        result = await gatherer.func(context)
                    else:
                        result = await gatherer.func()

                    if isinstance(result, Unfuture):
                        result = result.result()

                    if update_view_state_if_applicable(result, context):
                        log.debug("Initial state gathered")
                    else:
                        log.warning(f"No initial state has been gathered by {gatherer.name}")
                    return result

                except Exception as e:
                    raise GatherStepError(e)

            return gather_initial_state_async, is_coroutine

        else:

            def gather_initial_state(context: Context):
                log.debug(f"Gathering initial state via {gatherer.name}")
                try:
                    if requires_context:
                        result = gatherer.func(context)
                    else:
                        result = gatherer.func()

                    if isinstance(result, Unfuture):
                        result = result.result()

                    if update_view_state_if_applicable(result, context):
                        log.debug("Initial state gathered")
                    else:
                        log.warning(f"No initial state has been gathered by {gatherer.name}")
                    return result
                except Exception as e:
                    raise GatherStepError(e)

            return gather_initial_state, is_coroutine
