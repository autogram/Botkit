from typing import Set

from unsync import Unfuture

from botkit.routing.pipelines.factory_types import ICallbackStepFactory
from botkit.routing.pipelines.gatherer import (
    GathererSignature,
    GathererSignatureExamplesStr,
)
from botkit.routing.pipelines.steps._base import StepError
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.botkit_logging.setup import create_logger
from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import Context


class GatherStepError(StepError[GathererSignature]):
    pass


# noinspection PyMissingTypeHints
class GatherStepFactory(ICallbackStepFactory[GathererSignature]):
    @classmethod
    def applicable_update_types(cls) -> Set[UpdateType]:
        return {
            UpdateType.message,
            UpdateType.callback_query,
            UpdateType.inline_query,
            UpdateType.poll,
            UpdateType.user_status,
        }

    @classmethod
    def create_step(cls, gatherer: TypedCallable[GathererSignature]):
        if gatherer is None:
            return None, None

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

                    return result
                except Exception as e:
                    raise GatherStepError(e)

            return gather_initial_state, is_coroutine
