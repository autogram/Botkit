import inspect
from dataclasses import dataclass
from functools import reduce, wraps
from typing import Any, Awaitable, Callable, Generic, List, Protocol, Type, TypeVar, Union, cast

from injector import Injector, inject

from botkit.routing.pipelines_v2.base._abstractions import (
    MiddlewareChainer,
    Middleware,
    NextDelegate,
    TContext,
    chain_middleware,
)
from botkit.routing.pipelines_v2.base.scopes import EventScope
from botkit.routing.pipelines_v2.context_initializer import ContextInitializer


async def bottom_delegate(_: Any) -> None:
    print("Reached bottom!")


class EventPipeline(Generic[TContext]):
    def __init__(
        self,
        middleware: List[Union[Middleware[TContext], Type[Middleware[TContext]]]],
        injector: Injector,
        context_initializer: ContextInitializer,
        chain: MiddlewareChainer[TContext] = chain_middleware,
        bottom_delegate: NextDelegate[TContext] = bottom_delegate,
    ):
        self.delegates = middleware
        self.global_injector = injector
        self.initialize_context = context_initializer
        self.chain = chain
        self.bottom_delegate = bottom_delegate

    async def dispatch(self, event_type: Any, event_data: Any) -> None:
        context = self.initialize_context(event_type, event_data)
        EventScope(self.global_injector, context)

        instantiated_delegates = [
            self.global_injector.get(cast(Type[Middleware[TContext]], x))
            if inspect.isclass(x)
            else cast(Middleware[TContext], x)
            for x in self.delegate_types
        ]
        await self.chain(self.bottom_delegate, instantiated_delegates)(context)


inject(EventPipeline)  # type: ignore
