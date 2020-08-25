from typing import Generic, TypeVar

from botkit.utils.typed_callable import TypedCallable

T = TypeVar("T")


class StepError(Exception, Generic[T]):
    def __init__(self, inner_exception: Exception):
        super(StepError, self).__init__(inner_exception)
        self.with_traceback(inner_exception.__traceback__)
