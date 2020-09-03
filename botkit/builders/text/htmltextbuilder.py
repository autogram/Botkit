from html import escape as escape_html

from boltons.strutils import html2text
from typing import Any, cast

from botkit.builders.text.basetextbuilder import BaseTextBuilder


class _HtmlTextBuilder(BaseTextBuilder):
    def text(self, text: Any, end=""):
        return self._append_with_end(self.escape_html(text), end)

    @classmethod
    def as_text(cls, text: Any, end="") -> str:
        return cls._apply_end(cls.escape_html(text), end)

    def italic(self, text: Any, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "i", if_), end)

    @classmethod
    def as_italic(cls, text: Any, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "i", if_), end)

    def bold(self, text: Any, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "b", if_), end)

    @classmethod
    def as_bold(cls, text: Any, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "b", if_), end)

    def mono(self, text: Any, end="", if_: bool = True):
        return self.code(text, end, if_)

    def code(self, text: Any, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "code", if_), end)

    def mono_block(self, text: Any, end="", if_: bool = True):
        return self.code_block(text, end, if_)

    def code_block(self, text: Any, end="", if_: bool = True):
        return self._append(self.as_code_block(text, end, if_))

    @classmethod
    def as_mono(cls, text: Any, end="", if_: bool = True) -> str:
        return cls.as_code(text, end, if_)

    @classmethod
    def as_code(cls, text: Any, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "code", if_), end)

    @classmethod
    def as_mono_block(cls, text: Any, end="", if_: bool = True) -> str:
        return cls.as_code_block(text, end, if_)

    @classmethod
    def as_code_block(cls, text: Any, end="", if_: bool = True) -> str:
        text = f"\n{text}\n"
        return cls._apply_end(cls._wrap_and_escape(text, "code", if_), end)

    def strike(self, text: Any, end="", if_: bool = True):
        return self._append_with_end(self._wrap_and_escape(text, "s", if_), end)

    @classmethod
    def as_strike(cls, text: Any, end="", if_: bool = True) -> str:
        return cls._apply_end(cls._wrap_and_escape(text, "s", if_), end)

    def link(self, text: Any, href: str, end="", if_: bool = True):
        html = f'<a href="{href}">{self.escape_html(text)}</a>'
        return self._append_with_end(html, end)

    @classmethod
    def as_link(cls, text: Any, href: str, end="", if_: bool = True) -> str:
        html = f'<a href="{cls.escape_html(href)}">{cls.escape_html(text)}</a>'
        return cls._apply_end(html, end)

    @classmethod
    def _wrap_and_escape(cls, text: Any, tag: str, if_: bool = True) -> str:
        return cls._wrap_html(cls.escape_html(text), tag, if_)

    @staticmethod
    def escape_html(text: Any) -> str:
        if text is None:
            raise ValueError("Trying to append None value.")
        text = str(text)
        if not text:
            return cast(str, text)
        return html2text(str(text))

    @staticmethod
    def _wrap_html(text: Any, tag: str, if_: bool = True) -> str:
        if text is None:
            raise ValueError("Trying to append None value.")
        text = str(text)
        if not if_:
            return cast(str, text)
        return f"<{tag}>{text}</{tag}>"
