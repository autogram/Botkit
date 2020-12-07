import inspect
from abc import ABC, abstractmethod
from functools import reduce, wraps
from typing import Any, Awaitable, Callable, Coroutine, Generic, List, Protocol, TypeVar, cast

from pydantic import BaseModel

TContext = TypeVar("TContext")

NextDelegate = Callable[[TContext], Coroutine[Any, Any, None]]


# MiddlewareSignature = Callable[[TContext, NextDelegate[TContext]], Coroutine[Any, Any, Any]]


class Middleware(Protocol[TContext]):
    def __call__(
        self, context: TContext, call_next: NextDelegate[TContext]
    ) -> Coroutine[Any, Any, Any]:
        ...


class AbstractGenericMiddleware(ABC, Generic[TContext], Middleware[TContext]):
    @abstractmethod
    def __call__(
        self, context: TContext, call_next: NextDelegate[TContext]
    ) -> Coroutine[Any, Any, Any]:
        ...


# region Middleware chaining

MiddlewareChainer = Callable[
    [NextDelegate[TContext], List[Middleware[TContext]]], NextDelegate[TContext]
]
"""
Type annotation for a function that can be used to build a chain of middleware, with the
result being a single callback that execues all of the `delegates` recursively and the `bottom` last.
"""


def chain_middleware(
    bottom: NextDelegate[TContext], delegates: List[Middleware[TContext]]
) -> NextDelegate[TContext]:
    def wrap_next(
        acc: NextDelegate[TContext], nxt: Middleware[TContext]
    ) -> NextDelegate[TContext]:
        @wraps(nxt)
        async def await_and_next(ctx: TContext) -> None:
            try:
                res = nxt(ctx, acc)
                if inspect.isawaitable(res):
                    await cast(Awaitable[Any], res)
            except TypeError as te:
                if "missing 1 required positional argument" in str(te):
                    raise TypeError(
                        "Next middleware in pipeline has been called with incorrect arguments. "
                        "Make sure to pass on the context."
                    ) from te

        return await_and_next

    return reduce(wrap_next, reversed(delegates or []), bottom)


# endregion

# region Lifecycle


class LifecycleEvent(BaseModel):
    pass


class LifecycleEventHandler(AbstractGenericMiddleware[LifecycleEvent], ABC):
    ...


# endregion

# region Event pipeline


class PipelineContext(BaseModel):
    pass


class UpdatePipelineStep(AbstractGenericMiddleware[PipelineContext], ABC):
    pass


# endregion
