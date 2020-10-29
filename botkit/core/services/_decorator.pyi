from haps import base, egg, scope as haps_scope
from typing import Any, Callable, TypeVar, overload

_F = TypeVar("_F", bound=Any)


@overload
def service(class_: _F) -> _F:
    ...


@overload
def service(*, mode: str) -> Callable[[_F], _F]:
    ...



@service(mode="abc")
class Lala:
    x: int = 3


x: Lala = Lala()
