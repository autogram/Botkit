import inspect
from typing import Generic, Type, TypeVar, Union

from botkit.utils.typed_callable import TypedCallable

T = TypeVar("T")


class StepError(Exception, Generic[T]):
    def __init__(self, inner_exception: Exception):

        # TODO: Remove check
        assert not inspect.isclass(inner_exception)

        self.inner_exception = inner_exception
        super(StepError, self).__init__(inner_exception)
        self.with_traceback(inner_exception.__traceback__)

    @property
    def should_ignore_and_continue(self) -> bool:
        return isinstance(self.inner_exception, Continue)


class Continue(Exception):
    """
    Can be raised in intermediate steps of the pipeline in order to cancel the execution silently.
    """

    def __init__(self, reason: str = None):
        self.reason = reason
