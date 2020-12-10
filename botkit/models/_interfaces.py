from abc import ABC, abstractmethod

from botkit.botkit_context import Context
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    AbstractSet,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    AsyncIterator,
    AsyncIterable,
    Coroutine,
    Collection,
    AsyncGenerator,
    Deque,
    Dict,
    List,
    Set,
    FrozenSet,
    NamedTuple,
    Generator,
    cast,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import TypedDict

StateModel = TypeVar("StateModel")


class IGatherer(ABC):
    @classmethod
    @abstractmethod
    def create_from_context(cls, ctx: Context) -> "StateModel":
        ...
