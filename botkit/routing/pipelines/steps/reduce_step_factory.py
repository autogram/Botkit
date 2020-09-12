from functools import update_wrapper

from botkit.routing.pipelines.factory_types import ICallbackStepFactory
from botkit.routing.pipelines.steps._base import StepError
from botkit.routing.pipelines.reducer import ReducerSignature
from botkit.routing.pipelines.steps.helpers.state_generators import update_view_state_if_applicable
from botkit.utils.botkit_logging.setup import create_logger


class ReduceStepError(StepError[ReducerSignature]):
    pass


# noinspection PyMissingTypeHints
class ReduceStepFactory(ICallbackStepFactory[ReducerSignature]):
    @classmethod
    def create_step(cls, reducer):
        if not reducer:
            return None, None

        log = create_logger("reducer")
        is_coroutine = reducer.is_coroutine

        if is_coroutine:

            async def mutate_previous_state_async(previous_state, context):
                reducer_args = (
                    (previous_state,) if reducer.num_parameters == 1 else (previous_state, context)
                )

                try:
                    log.debug(f"Mutating state asynchronously using reducer {reducer.name}")
                    result = await reducer.func(*reducer_args)
                except Exception as e:
                    raise ReduceStepError(e)

                if update_view_state_if_applicable(result, context):
                    log.debug("View state mutated")
                else:
                    log.debug("No state transition required")
                return result

            update_wrapper(mutate_previous_state_async, ReduceStepFactory)
            return mutate_previous_state_async, is_coroutine
        else:

            def mutate_previous_state(previous_state, context):
                reducer_args = (
                    (previous_state,) if reducer.num_parameters == 1 else (previous_state, context)
                )

                try:
                    log.debug(f"Mutating state using reducer {reducer.name}")
                    result = reducer.func(*reducer_args)
                except Exception as e:
                    raise ReduceStepError(e)

                if update_view_state_if_applicable(result, context):
                    log.debug("View state mutated")
                else:
                    log.debug("No state transition required")
                return result

            update_wrapper(mutate_previous_state, ReduceStepFactory)
            return mutate_previous_state, is_coroutine
