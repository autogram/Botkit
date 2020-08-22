from typing import Awaitable, Callable, Union

from botkit.persistence.callback_manager import CallbackActionContext
from botkit.routing.types import ReturnType, TArg, TState

HandlerSignature = Union[
    # Plain library handler signatures
    Callable[[TArg, TArg], Awaitable[ReturnType]],
    Callable[[TArg, TArg, TArg, TArg], Awaitable[ReturnType]],
    # Library routes with states
    Callable[[TArg, TArg, CallbackActionContext], Awaitable[ReturnType]],
    Callable[[TArg, TArg, TArg, TArg, CallbackActionContext], Awaitable[ReturnType]],
]
