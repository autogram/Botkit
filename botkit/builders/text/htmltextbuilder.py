from html import escape as escape_html

from boltons.strutils import html2text
from typing import Any, Iterable, List, Optional, cast

from botkit.builders.text.basetextbuilder import BaseTextBuilder


class _HtmlTextBuilder(BaseTextBuilder):
    # region internals

    @staticmethod
    def escape_html(text: str) -> str:
        if text is None:
            raise ValueError("Trying to append None value.")
        text = str(text)
        if not text:
            return cast(str, text)
        return html2text(str(text))

    @classmethod
    def _wrap_html(cls, text: str, tag: str, if_: bool = True) -> str:
        if text is None:
            raise ValueError("Trying to append None value.")
        text = str(text)
        if not if_:
            return cast(str, text)
        return f"<{tag}>{text}</{tag}>"

    @classmethod
    def _wrap_and_escape(cls, text: str, tag: str, if_: bool = True) -> str:
        return cls._wrap_html(cls.escape_html(text), tag, if_)

    # endregion internals

    def text(self, text: str, end=""):
        return self._append_with_end(self.escape_html(text), end)

    @classmethod
    def as_text(cls, text: str, end="") -> str:
        return cls._apply_end(cls.escape_html(text), end)

    def italic(self, text: str, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "i", if_), end)

    @classmethod
    def as_italic(cls, text: str, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "i", if_), end)

    def bold(self, text: str, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "b", if_), end)

    @classmethod
    def as_bold(cls, text: str, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "b", if_), end)

    @classmethod
    def as_mono(cls, text: str, end="", if_: bool = True) -> str:
        return cls.as_code(text, end, if_)

    def mono(self, text: str, end="", if_: bool = True):
        return self.code(text, end, if_)

    @classmethod
    def as_code(cls, text: str, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "code", if_), end)

    def code(self, text: str, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "code", if_), end)

    @classmethod
    def as_mono_block(cls, text: str, end="", if_: bool = True) -> str:
        return cls.as_code_block(text, end, if_)

    def mono_block(self, text: str, end="", if_: bool = True):
        return self.code_block(text, end, if_)

    @classmethod
    def as_code_block(cls, text: str, end="", if_: bool = True) -> str:
        text = f"\n{text}\n"
        return cls._apply_end(cls._wrap_and_escape(text, "code", if_), end)

    def code_block(self, text: str, end="", if_: bool = True):
        return self._append(self.as_code_block(text, end, if_))

    @classmethod
    def as_strike(cls, text: str, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "s", if_), end)

    def strike(self, text: str, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "s", if_), end)

    @classmethod
    def as_link(cls, text: str, href: str, end="") -> str:
        html = f'<a href="{cls.escape_html(href)}">{cls.escape_html(text)}</a>'
        return cls._apply_end(html, end)

    def link(self, text: str, href: str, end=""):
        html = f'<a href="{href}">{self.escape_html(text)}</a>'
        return self._append_with_end(html, end)
