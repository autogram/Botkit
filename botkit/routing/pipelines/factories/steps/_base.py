from typing import Generic, TypeVar

from botkit.utils.typed_callable import TypedCallable

T = TypeVar("T")


class StepError(Exception, Generic[T]):
    def __init__(self, func: TypedCallable[T]):
        self.func = func
