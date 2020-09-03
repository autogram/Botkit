from typing import Iterable

from haps import Container
from pytest import fixture
from types import ModuleType


@fixture(scope="module")
def di():
    def inner(*modules):
        assert all((isinstance(x, ModuleType) for x in modules))
        Container._reset()
        Container.autodiscover([x.__name__ for x in modules])

    return inner
