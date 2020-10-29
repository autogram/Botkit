import warnings
import inspect
from dataclasses import dataclass

from cached_property import cached_property
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Mapping,
    Protocol,
    Tuple,
    TypeVar,
    get_type_hints,
)

# TArgs = TypeVar("TArgs", bound=Any)
# TKwds = TypeVar("TKwds", bound=Any)
# TRet = TypeVar("TRet", bound=Any)


# class Func(Protocol[TArgs, TKwds, TRet]):
#     __name__: str

#     def __call__(self, *args: TArgs, **kwds: TKwds) -> TRet:
#         ...


# T = TypeVar("T", bound=Func)


# class FuncWrapper(Generic[TArgs, TKwds, TRet]):
#     def __init__(self, func: Func[TArgs, TKwds, TRet]) -> None:
#         self.func = func

#     def __call__(self, *args: TArgs, **kwds: Dict[str, Any]) -> TRet:
#         return self.func(*args, **kwds)

#     @cached_property
#     def name(self) -> str:
#         return self.func.__name__


class Func(Protocol):
    __name__: str
    __call__: Callable[..., Any]


T = TypeVar("T", bound=Func)


@dataclass(frozen=True)
class TypedCallable(Generic[T]):
    func: T

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.func(*args, **kwds)

    @property
    def name(self) -> str:
        return self.func.__name__

    @cached_property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

    @cached_property
    def parameters(self) -> Mapping[str, inspect.Parameter]:
        return inspect.signature(self.func).parameters

    @cached_property
    def is_coroutine(self) -> bool:
        result = inspect.iscoroutinefunction(self.func)
        if not result and inspect.isawaitable(result):
            # Generally, we don't want to have anything to do with asyncio futures, tasks, and the like.
            warnings.warn(
                f"Callable {self.name} is a {type(self.func)}, which is awaitable, but not a coroutine (async "
                f"def). It is possible that you will always get the same result when it is awaited."
            )
            return True
        return result

    @cached_property
    def type_hints(self) -> Dict[str, Any]:
        return get_type_hints(self.func)

    @cached_property
    def num_parameters(self) -> int:
        return len(self.parameters)

    @cached_property
    def num_non_optional_params(self) -> int:
        return sum((1 for p in self.parameters.values() if p.default is p.empty))

    def __str__(self) -> str:
        return str(self.func)
