from typing import (
    Any,
    Callable,
)

import pytest
from haps import Egg, egg

from botkit.core import modules
from botkit.core.modules import module
from botkit.routing.route_builder.builder import RouteBuilder


@pytest.yield_fixture(scope="function")
def get_single_module() -> Callable[[], Any]:
    print("resetting")
    egg.factories = []

    def inner():
        print("GETTING")
        m = modules.haps_disambiguate_module_eggs()
        assert len(m) <= 1, "More than one module found!"
        assert m, "No module found!"
        return m[0]

    yield inner
    print("teardown")
    egg.factories = []


def test_func_can_be_decorated(get_single_module):
    @module("OpenInBrowserModule")
    def _(routes: RouteBuilder) -> None:
        pass  # TODO

    actual = get_single_module()

    assert actual.base_ is modules.Module
    assert actual.type_.__name__ == "OpenInBrowserModule"


def test_func_decorator_without_name(get_single_module):
    def my_module(routes: RouteBuilder):
        pass  # TODO

    # Fake decorator
    decorated = module(my_module)(None)

    actual = get_single_module()

    assert actual.qualifier == "MyModule", f"{actual.qualifier} != MyModule"


def test_func_decorator_can_be_called(get_single_module):
    def my_module(routes: RouteBuilder):
        pass

    # Fake decorator
    decorated = module(my_module)(None)

    actual: Egg = get_single_module()

    assert issubclass(actual.type_, modules.Module)

    initialized = actual.type_()
    assert isinstance(initialized, modules.Module)


def test_func_decorator_missing_route_builder_fails(get_single_module):
    def my_module():
        pass

    # Fake decorator
    decorated = module(my_module)()

    actual = get_single_module()

    instance = actual.type_()

    with pytest.raises(TypeError) as ex:
        instance.register(RouteBuilder())

        # TODO: Add error handling, "your register function should have a RouteBuilder
    print(ex.value)


# def test_load_args_can_be_passed():
#     @module("TestModule", load="test", unload=)
#     def my_module(routes: RouteBuilder):
#         pass
