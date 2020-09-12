import inspect
from typing import Awaitable, Callable, Union, List

from botkit.routing.types import TViewState
from botkit.views.botkit_context import Context

ReducerSignature = Union[
    Callable[[TViewState, Context], Union[TViewState, Awaitable[TViewState]]],
    Callable[[TViewState], Union[TViewState, Awaitable[TViewState]]],
    Callable[[TViewState, Context], Union[None, Awaitable]],
    Callable[[TViewState], Union[None, Awaitable]],
]
ReducerSignatureExamplesStr = str(ReducerSignature)
