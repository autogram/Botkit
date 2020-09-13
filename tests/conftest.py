from typing import Iterable

from haps import Container
from pytest import fixture
from types import ModuleType


@fixture(scope="function", autouse=True)
def reset_container():
    Container._reset()
    yield
    Container._reset()


# @fixture(scope="function")
# def di():
#     def inner(*modules):
#         assert all((isinstance(x, ModuleType) for x in modules))
#         Container.autodiscover([x for x in modules])
#         print(modules, Container().config)
#
#     return inner
