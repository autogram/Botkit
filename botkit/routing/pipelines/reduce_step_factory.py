from typing import Awaitable, Callable, Optional, Union

from botkit.routing.pipelines.factory_types import ICallbackStepFactory
from botkit.routing.pipelines.reducer import ReducerSignature
from botkit.routing.types import TState
from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import BotkitContext

class ReduceStepError(Exception):
    def __init__(self, reducer: TypedCallable[ReducerSignature]):
        self.reducer = reducer


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

                # XXX: If we check for type(choices) aswell, you can't change the choices in a reducer
                return new_state if new_state is not None else previous_state

            return mutate_previous_state_async, is_coroutine
        else:

            def mutate_previous_state(previous_state, context):
                reducer_args = (previous_state,) if reducer.num_parameters == 1 else (previous_state, context)

                try:
                    new_state = reducer.func(*reducer_args)
                except Exception as e:
                    raise ReduceStepError(reducer) from e

                # XXX: If we check for type(choices) aswell, you can't change the choices in a reducer
                return new_state if new_state is not None else previous_state

            return mutate_previous_state, is_coroutine
