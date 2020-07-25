from typing import Any, Awaitable, Callable, Union

from unsync import Unfuture

from botkit.routing.pipelines.factory_types import ICallbackStepFactory
from botkit.routing.types import TState

# noinspection PyMissingTypeHints
from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import BotkitContext

GathererSignature = Union[
    Callable[[], Union[Any, Awaitable[TState]]], Callable[[BotkitContext], Union[Any, Awaitable[TState]]]
]
GathererSignatureExamplesStr = """
- def () -> TState
- def (context: BotkitContext) -> TState
- async def () -> TState
- async def (context: BotkitContext) -> TState
""".strip()
GathererSignatureExamplesStr = str(GathererSignature)

# noinspection PyMissingTypeHints
class GatherStepFactory(ICallbackStepFactory[GathererSignature]):
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

        is_coroutine = gatherer.is_coroutine

        if is_coroutine:

            async def gather_initial_state_async(context: BotkitContext):
                try:
                    if requires_context:
                        result = await gatherer.func(context)
                    else:
                        result = await gatherer.func()

                    if isinstance(result, Unfuture):
                        result = result.result()

                    return result
                except Exception as e:
                    raise GatherStepError(gatherer) from e

            return gather_initial_state_async, is_coroutine

        else:

            def gather_initial_state(context: BotkitContext):
                try:
                    if requires_context:
                        result = gatherer.func(context)
                    else:
                        result = gatherer.func()

                    if isinstance(result, Unfuture):
                        result = result.result()

                    return result
                except Exception as e:
                    raise GatherStepError(gatherer) from e

            return gather_initial_state, is_coroutine


class GatherStepError(Exception):
    def __init__(self, gatherer: TypedCallable[GathererSignature]):
        self.gatherer = gatherer
