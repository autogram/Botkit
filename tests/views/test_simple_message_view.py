from typing import Iterable

from dataclasses import dataclass
from pyrogram import InlineKeyboardButton



def test_simple_message_view_can_be_instantiated():
    TestMessageViewSimple(MyModel(test_string="teststring"), context=ViewContext())


def test_simple_message_view_can_be_rendered():
    view = TestMessageViewSimple(MyModel(test_string="teststring"), context=ViewContext())
    rendered = view._render()
    assert rendered.text == "teststring"
    assert rendered.buttons is None


@dataclass
class MyModel:
    test_string: str


class TestMessageViewSimple(MessageView[MyModel]):
    def render_body(self):
        return self.state.test_string

    def render_inline_menu(self) -> Iterable[Iterable[KeyboardTypes]]:
        return [[InlineKeyboardButton("test", callback_data="test")]]
