from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Callable, Generic, Optional, Tuple, TypeVar

from pyrogram import Update

from botkit.utils.typed_callable import TypedCallable

TState = TypeVar("TState")

TUserInput = TypeVar("TUserInput")
TResult = TypeVar("TResult")

TFunc = TypeVar("TFunc", bound=Callable)


class IStepFactory(Generic[TUserInput, TResult], ABC):
    @classmethod
    @abstractmethod
    def create_step(cls, user_input: Optional[TUserInput]) -> TResult:
        ...


# This could inherit from IStepFactory, but that breaks PyCharm's type inference and makes it unnecessarily hard to
# understand.
class ICallbackStepFactory(Generic[TFunc], ABC):
    @classmethod
    @abstractmethod
    def create_step(cls, user_defined_func: Optional[TypedCallable[TFunc]]) -> Tuple[Optional[TFunc], Optional[bool]]:
        ...
