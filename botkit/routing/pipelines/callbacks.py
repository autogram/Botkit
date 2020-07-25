from typing import Awaitable, Callable, Union

from botkit.dispatching.callbackqueries.callback_manager import CallbackActionContext
from botkit.routing.types import ReturnType, TArg, TState

CallbackSignature = Union[
    # Plain Pyrogram handler signatures
    Callable[[TArg, TArg], Awaitable[ReturnType]],
    Callable[[TArg, TArg, TArg, TArg], Awaitable[ReturnType]],
    # Pyrogram routes with models
    Callable[[TArg, TArg, TState, CallbackActionContext], Awaitable[ReturnType]],
    Callable[[TArg, TArg, TArg, TArg, TState, CallbackActionContext], Awaitable[ReturnType]],
]
