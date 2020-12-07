from typing import Literal, Type, TypeVar, Union, overload


X = TypeVar("X")

@overload
def isclass(obj: Type[X]) -> Literal[True]:
    ...


@overload
def isclass(obj: X) -> Literal[False]:
    ...
