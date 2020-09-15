from typing import Iterable

from haps import Container
from pytest import fixture
from types import ModuleType


@fixture(scope="function", autouse=True)
def reset_container():
    Container._reset()
    yield
    Container._reset()

