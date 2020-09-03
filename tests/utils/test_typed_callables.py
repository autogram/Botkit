import inspect
from typing import Optional, Union

from pyrogram.types import Message

from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import Context


def my_func(ctx: Context, test_int: int = 1, test_none: Optional[str] = None):
    pass


async def my_func_async(ctx: Context, test_int: int = 1, test_none: Optional[str] = None):
    pass


class TestClass:
    def my_method(self, ctx: Context, test_int: int = 1, test_none: Optional[str] = None):
        pass

    async def my_method_async(
        self, ctx: Context, test_int: int = 1, test_none: Optional[str] = None
    ):
        pass


def test_regular_function_properties():
    tc = TypedCallable(my_func)
    assert not tc.is_coroutine
    assert tc.name == "my_func"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {"ctx": Context, "test_int": int, "test_none": Optional[str]}


def test_coroutine_function_properties():
    tc = TypedCallable(my_func_async)
    assert tc.is_coroutine
    assert tc.name == "my_func_async"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {"ctx": Context, "test_int": int, "test_none": Optional[str]}


def test_regular_method_properties():
    cls = TestClass()
    tc = TypedCallable(cls.my_method)
    assert not tc.is_coroutine
    assert tc.name == "my_method"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {"ctx": Context, "test_int": int, "test_none": Optional[str]}


def test_coroutine_method_properties():
    cls = TestClass()
    tc = TypedCallable(cls.my_method_async)
    assert tc.is_coroutine
    assert tc.name == "my_method_async"
    assert tc.num_non_optional_params == 1
    assert tc.num_parameters == 3
    assert tc.type_hints == {"ctx": Context, "test_int": int, "test_none": Optional[str]}


def test_sth():
    m = Message(message_id=123)
    edit_sig = inspect.signature(m.edit)
    reply_sig = inspect.signature(m.reply)
    assert edit_sig == reply_sig
