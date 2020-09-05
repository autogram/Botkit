from functools import update_wrapper

from botkit.routing.pipelines.factory_types import ICallbackStepFactory
from botkit.routing.pipelines.steps._base import StepError
from botkit.routing.pipelines.reducer import ReducerSignature
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
                    (previous_state,)
                    if reducer.num_parameters == 1
                    else (previous_state, context)
                )

                try:
                    log.debug(
                        f"Mutating state asynchronously using reducer {reducer.name}"
                    )
                    new_state = await reducer.func(*reducer_args)
                except Exception as e:
                    raise ReduceStepError(e)

                # XXX: If we check for type(choices) aswell, you can't change the choices in a handler
                return new_state if new_state is not None else previous_state

            update_wrapper(mutate_previous_state_async, ReduceStepFactory)
            return mutate_previous_state_async, is_coroutine
        else:

            def mutate_previous_state(previous_state, context):
                reducer_args = (
                    (previous_state,)
                    if reducer.num_parameters == 1
                    else (previous_state, context)
                )

                try:
                    log.debug(f"Mutating state using reducer {reducer.name}")
                    new_state = reducer.func(*reducer_args)
                except Exception as e:
                    raise ReduceStepError(e)

                # XXX: If we check for type(choices) aswell, you can't change the choices in a handler
                return new_state if new_state is not None else previous_state

            update_wrapper(mutate_previous_state, ReduceStepFactory)
            return mutate_previous_state, is_coroutine
