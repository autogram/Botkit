from botkit.routing.pipelines.factories.factory_types import ICallbackStepFactory
from botkit.routing.pipelines.factories.steps._base import StepError
from botkit.routing.pipelines.reducer import ReducerSignature
from botkit.utils.typed_callable import TypedCallable


class ReduceStepError(StepError[ReducerSignature]):
    pass


# noinspection PyMissingTypeHints
class ReduceStepFactory(ICallbackStepFactory[ReducerSignature]):
    @classmethod
    def create_step(cls, reducer):
        if not reducer:
            return None, None

        is_coroutine = reducer.is_coroutine

        if is_coroutine:

            async def mutate_previous_state_async(previous_state, context):
                reducer_args = (previous_state,) if reducer.num_parameters == 1 else (previous_state, context)

                try:
                    new_state = await reducer.func(*reducer_args)
                except Exception as e:
                    raise ReduceStepError(reducer) from e

                # XXX: If we check for type(choices) aswell, you can't change the choices in a handler
                return new_state if new_state is not None else previous_state

            return mutate_previous_state_async, is_coroutine
        else:

            def mutate_previous_state(previous_state, context):
                reducer_args = (previous_state,) if reducer.num_parameters == 1 else (previous_state, context)

                try:
                    new_state = reducer.func(*reducer_args)
                except Exception as e:
                    raise ReduceStepError(reducer) from e

                # XXX: If we check for type(choices) aswell, you can't change the choices in a handler
                return new_state if new_state is not None else previous_state

            return mutate_previous_state, is_coroutine
