from pyrogram import Client, Message, CallbackQuery, InlineQuery, Poll
from typing import Any, Optional, TypeVar, Union, Iterable

TState = TypeVar("TState")

TClient = TypeVar("TClient", bound=Client)
TMessage = TypeVar("TMessage", bound=Message)
TCallbackQuery = TypeVar("TCallbackQuery", bound=CallbackQuery)
TInlineQuery = TypeVar("TInlineQuery", bound=InlineQuery)
TPoll = TypeVar("TPoll", bound=Poll)
TDeletedMessages = TypeVar("TDeletedMessages", bound=Iterable[Message])

ReturnType = Optional[Union["_ViewBase", Any]]

TArg = Union[TClient, TMessage, TCallbackQuery, TInlineQuery, TPoll]



