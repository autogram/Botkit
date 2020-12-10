import inspect
from typing import Any, List, Type, TypeVar, Union

from injector import (
    Binder,
    CallableProvider,
    Injector,
    InstanceProvider,
    Module,
    SingletonScope,
    inject,
    multiprovider,
)

from botkit.botkit_context import Context
from botkit.routing.pipelines_v2.base._abstractions import (
    Middleware,
    MiddlewareChainer,
    NextDelegate,
    chain_middleware,
)
from botkit.routing.pipelines_v2.base.middleware import BaseMiddleware
from botkit.routing.pipelines_v2.eventpipeline import EventPipeline
from botkit.routing.pipelines_v2.middleware.gather_step_factory import GathererMiddleware
from botkit.routing.pipelines_v2.middleware.pydepend import Dependency

T = TypeVar("T")
ClassOrInstance = Union[T, Type[T]]


class EventPipelinesModule(Module):
    def configure(self, binder: Binder):
        binder.bind(EventPipeline)
        binder.bind(
            MiddlewareChainer, InstanceProvider(chain_middleware), SingletonScope  # type: ignore
        )


def register_middleware(
    binder: Binder,
    middleware: ClassOrInstance[Middleware],
    depends_on: List[ClassOrInstance[Middleware]],
):
    injector = binder.injector.get(Injector)

    if inspect.isclass(middleware):
        binder.bind(middleware, scope=SingletonScope)
        binder.multibind(
            List[Dependency[Middleware]],
            CallableProvider(
                lambda: [
                    Dependency(
                        injector.get(middleware),
                        deps=[Dependency(injector.get(middleware)) for d in depends_on],
                    )
                ]
            ),
            scope=SingletonScope,
        )
    elif callable(middleware):
        binder.bind(middleware, InstanceProvider(middleware), SingletonScope)
        binder.multibind(
            List[Dependency[Middleware]],
            CallableProvider(
                lambda: [
                    Dependency(
                        injector.get(middleware),
                        deps=[Dependency(injector.get(middleware)) for d in depends_on],
                    )
                ]
            ),
            scope=SingletonScope,
        )


class A(BaseMiddleware):
    async def __call__(self, context: Context, call_next: NextDelegate[Context]) -> Any:
        pass


async def my_middleware(context: Context, call_next: NextDelegate[Context]) -> Any:
    pass


class PrebuiltMiddlewareModule(Module):
    def configure(self, binder: Binder) -> None:
        register_middleware(binder, GathererMiddleware, [A])
        register_middleware(binder, A, [])
        register_middleware(binder, my_middleware, [])

    @multiprovider
    def list_middleware_ordered(
        self, all_dependencies: List[Dependency[Middleware]]
    ) -> List[Middleware[Context]]:
        print(x.direct_deps for x in all_dependencies)
        return [(x, x.ordered_deps) for x in all_dependencies]
        # result = []
        # for x in all_dependencies:
        #     deps = x.ordered_deps
        #
        #     if x in result:
        #         pass
        #
        #     else:


class RoutingModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(Injector, binder.injector)
        binder.install(EventPipelinesModule)
        binder.install(PrebuiltMiddlewareModule)


if __name__ == "__main__":
    inj = Injector([PrebuiltMiddlewareModule])
    print(inj.get(List[Middleware[Context]]))
