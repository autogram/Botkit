import inspect
from typing import Awaitable, Callable, Union, List

from botkit.routing.types import TState
from botkit.views.botkit_context import Context

ReducerSignature = Union[
    Callable[[TState, Context], Union[TState, Awaitable[TState]]],
    Callable[[TState], Union[TState, Awaitable[TState]]],
    Callable[[TState, Context], Union[None, Awaitable]],
    Callable[[TState], Union[None, Awaitable]],
]
ReducerSignatureExamplesStr = str(ReducerSignature)
