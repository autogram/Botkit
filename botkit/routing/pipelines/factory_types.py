from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import astuple, dataclass
from typing import (
    Any,
    Callable,
    Generic,
    List,
    NamedTuple,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
)

from boltons.typeutils import classproperty

from tgtypes.updatetype import UpdateType
from botkit.utils.typed_callable import TypedCallable

TViewState = TypeVar("TViewState")

TData = TypeVar("TData")
TResult = TypeVar("TResult")

TFunc = TypeVar("TFunc", bound=Callable)


class MaybeAsyncPipelineStep(Tuple[Optional[TFunc], Optional[bool]], Generic[TFunc]):
    ...


class IPipelineStep(ABC):
    async def __call__(self, *args, **kwargs) -> Any:
        pass


# @abstractmethod
# async def __call__(self, *args, **kwargs):
#     pass


class IStepFactory(Generic[TData, TResult], ABC):
    """
    Interface to be implemented by any pipeline step factory that pregenerates a function to handle some functionality
    based on input parameters.
    """

    @classmethod
    @abstractmethod
    def create_step(cls, data: Optional[TData]) -> TResult:
        ...

    @classproperty
    def applicable_update_types(cls) -> Set[UpdateType]:
        return UpdateType.all


class ICallbackStepFactory(
    IStepFactory[TypedCallable[TFunc], MaybeAsyncPipelineStep[TFunc]], Generic[TFunc], ABC
):
    """
    Interface to be implemented by pipeline steps that operate on some callable, which needs to be wrapped in a
    `TypedCallable`.
    """

    @classmethod
    @abstractmethod
    def create_step(cls, func: Optional[TypedCallable[TFunc]]) -> MaybeAsyncPipelineStep[TFunc]:
        """
        Generates a pipeline step based on a (possibly user-defined) callable. If the callable is async, the second
        tuple return value will indicate this.
        :param func:
        :type func:
        :return:
        :rtype:
        """
