from typing import Iterable, Protocol, Type, TypeVar, Union

T = TypeVar("T")

X = Union[T, Iterable[T]]

d: X = 3


class MaybeMany(Protocol[T]):
    def __class_getitem__(cls, item: Type[T]) -> Union[T, Iterable[T]]:
        ...


x: MaybeMany[int] = 3
