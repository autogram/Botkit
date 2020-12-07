from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    Union,
)

from botkit.agnostic.library_checks import is_installed
from botkit.botkit_context import Context

if TYPE_CHECKING:
    from botkit.clients.client import IClient
else:
    IClient = None


if is_installed("pyrogram"):
    from pyrogram import Client
    from pyrogram.types import CallbackQuery, InlineQuery, Message, Poll

    TClient = TypeVar("TClient", bound=Client)
    TMessage = TypeVar("TMessage", bound=Message)
    TCallbackQuery = TypeVar("TCallbackQuery", bound=CallbackQuery)
    TInlineQuery = TypeVar("TInlineQuery", bound=InlineQuery)
    TPoll = TypeVar("TPoll", bound=Poll)
    TDeletedMessages = TypeVar("TDeletedMessages", bound=Iterable[Message])

    ReturnType = Optional[Union["_ViewBase", Any]]

    TArg = Union[IClient, TClient, TMessage, TCallbackQuery, TInlineQuery, TPoll]

    HandlerSignature = Union[
        # Plain library handler signatures
        Callable[[TArg, TArg], Awaitable[ReturnType]],
        Callable[[TArg, TArg, TArg, TArg], Awaitable[ReturnType]],
        # Library routes with botkit context as last arg
        Callable[[TArg, TArg, Context], Awaitable[ReturnType]],
        Callable[[TArg, TArg, TArg, TArg, Context], Awaitable[ReturnType]],
    ]


else:
    raise ValueError("No supported Python bot library found in installed modules.")
