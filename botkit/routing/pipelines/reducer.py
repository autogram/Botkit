import inspect
from typing import Awaitable, Callable, Union, List

from botkit.routing.types import TState
from botkit.views.botkit_context import BotkitContext

ReducerSignature = Union[
    Callable[[TState, BotkitContext], Union[TState, Awaitable[TState]]],
    Callable[[TState], Union[TState, Awaitable[TState]]],
    Callable[[TState, BotkitContext], Union[None, Awaitable]],
    Callable[[TState], Union[None, Awaitable]],
]
ReducerSignatureExamplesStr = str(ReducerSignature)
