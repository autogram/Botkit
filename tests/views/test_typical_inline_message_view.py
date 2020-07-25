from typing import Iterable

# noinspection Mypy
from dataclasses import dataclass
from pyrogram import InlineKeyboardButton


TextVi

@dataclass
class InlineModel:
    text: str
    title: str
    description: str
    menu: Iterable[Iterable[InlineKeyboardButton]]


class TypicalInlineView(TextView[InlineModel]):
    def render_body(self) -> str:
        return self.state.test

    def render_title(self) -> str:
        return self.state.title

    def render_description(self) -> str:
        return self.state.description

    def render_inline_menu(self) -> Iterable[Iterable[KeyboardTypes]]:
        return self.state.menu


def test_view_can_be_initialized():
    TypicalInlineView(InlineModel(text="", title="", description="", menu=[[]]), context=ViewContext())


def test_view_renders_correctly():
    view = TypicalInlineView(
        InlineModel(
            text="text",
            title="title",
            description="description",
            menu=[[InlineKeyboardButton("hello world", callback_data="test")]],
        )
    )
    rendered = view._render()
    assert rendered.text == "text"
    assert rendered.title == "title"
    assert rendered.description == "description"
    assert rendered.buttons is not None
    assert rendered.buttons[0][0].callback_data == "test"
    assert rendered.buttons[0][0].text == "hello world"
