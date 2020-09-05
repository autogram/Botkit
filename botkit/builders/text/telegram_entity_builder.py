from typing import Optional
from urllib.parse import urlencode

from boltons import strutils

from botkit.builders.text.basetextbuilder import BaseTextBuilder


class TelegramEntityBuilder(BaseTextBuilder):
    @classmethod
    def as_command(cls, name: str, to_lower: bool = False):
        name = name.lstrip("/")
        name = strutils.slugify(name, delim="", lower=to_lower, ascii=True).decode(
            "utf-8"
        )
        return f"/{name}"

    def command(self, name: str, to_lower: bool = False, end: Optional[str] = " "):
        return self._append_with_end(self.as_command(name=name, to_lower=to_lower), end)

    @classmethod
    def as_prompt(cls, text) -> "str":
        text = urlencode(text)
        return f"https://telegram.me/share/url?url={text}"
