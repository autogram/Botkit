from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, Tuple, TypeVar

from boltons.typeutils import classproperty
from pyrogram import Update

from botkit.routing.update_types.updatetype import UpdateType
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

    @property
    @abstractmethod
    def applicable_update_types(self) -> List[UpdateType]:
        ...


# This could inherit from IStepFactory, but that breaks PyCharm's type inference and makes it unnecessarily hard to
# understand. Let's see where this overengineered pile of ridiculousness goes in the future and reconsider at a later
# time.
class ICallbackStepFactory(Generic[TFunc], ABC):
    @classmethod
    @abstractmethod
    def create_step(
        cls, user_defined_func: Optional[TypedCallable[TFunc]]
    ) -> Tuple[Optional[TFunc], Optional[bool]]:
        ...

    @classmethod
    @classproperty
    @abstractmethod
    def applicable_update_types(cls) -> List[UpdateType]:
        ...
