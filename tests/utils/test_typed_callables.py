from typing import Any, Optional, Union


from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import Context


def my_func_1(ctx: Context[Any, Any], test_int: int = 1, test_none: Optional[str] = None) -> Any:
    pass


async def my_func_async(
    ctx: Context[Any, Any], test_int: int = 1, test_none: Optional[str] = None
):
    pass


class TestClass:
    def my_method(
        self, ctx: Context[Any, Any], test_int: int = 1, test_none: Optional[str] = None
    ):
        pass

    async def my_method_async(
        self, ctx: Context[Any, Any], test_int: int = 1, test_none: Optional[str] = None
    ):
        pass


def test_regular_function_properties():
    tc = TypedCallable(my_func_1)
    assert not tc.is_coroutine
    assert tc.name == "my_func_1"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {
        "ctx": Context[Any, Any],
        "test_int": int,
        "test_none": Optional[str],
        "return": Any
    }


def test_coroutine_function_properties():
    tc = TypedCallable(my_func_async)
    assert tc.is_coroutine
    assert tc.name == "my_func_async"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {
        "ctx": Context[Any, Any],
        "test_int": int,
        "test_none": Union[str, None],
    }


def test_regular_method_properties():
    cls = TestClass()
    tc = TypedCallable(cls.my_method)
    assert not tc.is_coroutine
    assert tc.name == "my_method"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {
        "ctx": Context[Any, Any],
        "test_int": int,
        "test_none": Optional[str],
    }


def test_coroutine_method_properties():
    cls = TestClass()
    tc = TypedCallable(cls.my_method_async)
    assert tc.is_coroutine
    assert tc.name == "my_method_async"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {
        "ctx": Context[Any, Any],
        "test_int": int,
        "test_none": Optional[str],
    }
