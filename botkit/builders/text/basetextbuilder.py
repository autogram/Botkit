from pprint import pprint
from haps import Container
from typing import Any, Optional, TypeVar

from pyrogram.parser import Parser
from pyrogram.types.messages_and_media.message import Str

from botkit.builders.callbackbuilder import CallbackBuilder
from botkit.persistence.callback_store import ICallbackStore
from botkit.settings import botkit_settings

TState = TypeVar("TState")


class BaseTextBuilder:
    def __init__(self, callback_builder: CallbackBuilder):  # TODO: make non-optional
        self.parts = []
        self.callback_builder = callback_builder

    @property
    def is_dirty(self) -> bool:
        return bool(self.parts)

    def raw(self, text: str, end=""):
        return self._append_with_end(text, end)

    def spc(self):
        self.parts.append(" ")
        return self

    def br(self, count: int = 1):
        self.parts.append("\n" * count)
        return self

    def para(self):
        self.parts.append("\n\n")
        return self

    def _append(self, text: str):
        self.parts.append(text)
        return self

    def _append_with_end(self, text: str, end: Optional[str]):
        self.parts.append(self._apply_end(text, end))
        return self

    @staticmethod
    def _apply_end(text: str, end: Optional[str]) -> str:
        if text is None:
            raise ValueError("Trying to append None value.")

        text = str(text)

        if text is None:
            raise ValueError(f"Cannot append '{text}' to message.")
        if end in ["", None]:
            return text
        else:
            return text + str(end)

    def render_html(self) -> str:
        result = "".join(self.parts)
        if not result or result.isspace():
            return "\xad"  # zero-width char
        return result

    async def render_and_parse(self) -> Str:
        res = await (Parser(None)).parse(self.render_html(), "html")
        return Str(res["message"]).init(res["entities"])
