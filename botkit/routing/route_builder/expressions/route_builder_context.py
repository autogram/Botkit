from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

TLoadResult = TypeVar("TLoadResult")


@dataclass
class RouteBuilderContext(Generic[TLoadResult]):
    load_result: Optional[Any] = None
    """
    Contains the return value of a module's asynchronous `load()` method so that the synchronous `register` has
    access to data that should be retrieved from a coroutine.
    """
