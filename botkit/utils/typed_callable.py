import inspect
import warnings
from dataclasses import dataclass

from cached_property import cached_property
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Protocol,
    TypeVar,
    Union,
    get_type_hints,
)


T = TypeVar("T", bound=Callable)


@dataclass(frozen=True)
class TypedCallable(Generic[T]):
    func: T

    @cached_property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

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
        return len(self.signature.parameters)

    @cached_property
    def num_non_optional_params(self) -> int:
        return sum((1 for p in self.signature.parameters.values() if p.default is p.empty))

    @cached_property
    def name(self) -> str:
        return self.func.__name__

    def __call__(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.func)
