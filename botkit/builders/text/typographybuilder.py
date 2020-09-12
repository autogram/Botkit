from typing import Iterable, Optional

from botkit.builders.text.emoji import Emoji
from botkit.builders.text.htmltextbuilder import _HtmlTextBuilder
from botkit.builders.text.iconographybuilder import Iconography, IconographyBuilder


class IconSettings:
    # The unordered list icon to use.
    list_icon = "▪"

    # Whether to render a space between unordered list icon and text.
    should_use_space_after_list_icon: bool = False


class TypographyBuilder(_HtmlTextBuilder, IconographyBuilder):
    icons = IconSettings

    def h1(self, title: str):
        self.parts.append(f"▶️ ")
        self.bold(title)
        self.para()
        return self

    def h3(self, title: str):
        self.bold(title.upper(), end=".")
        self.para()
        return self

    def headline(self, title: str, level: int):
        if level == 1:
            return self.h1(title)
        raise ValueError("No such headline level.", level)

    def smallcaps(self, text: str, end=""):
        return self._append_with_end(text, end)

    def enforce_min_width(self, width: int):
        self.code_block(" " * width + Iconography.ZERO_WIDTH_WHITESPACE)

    @classmethod
    def as_success(cls, text):
        return "{} {}".format(Emoji.white_check_mark, text, hide_keyboard=True)

    @classmethod
    def as_love(cls, text):
        return "💖 {}".format(text, hide_keyboard=True)

    @classmethod
    def as_failure(cls, text):
        return "{} {}".format(Emoji.cross_heavy, text)

    @classmethod
    def as_action_hint(cls, text):
        return "💬 {}".format(text)

    @classmethod
    def as_none_action(cls, text):
        return "{} {}".format(Emoji.negative_squared_cross_mark, text)

    @classmethod
    def as_cta(cls, text):
        """ Call-to-action """
        return cls.as_underline(cls.as_action_hint(text))

    def cta(self, call_to_action: str, end: Optional[str] = "\n"):
        self._append_with_end(self.as_cta(call_to_action), end)
        return self

    # region lists and list items

    @classmethod
    def as_list_item(cls, text: str) -> str:
        return f"{cls.icons.list_icon}{text.strip()}"

    def list_item(self, text: str, end: Optional[str] = None):
        return self._append_with_end(self.as_list_item(text), end).br()

    def list(self, items: Iterable[str]):
        for i in items:
            self.list_item(text=i)
        return self

    @classmethod
    def as_numbered_list_item(cls, text: str, n: int, use_emoji_numbers: bool = True) -> str:
        if use_emoji_numbers:
            return f"{cls.as_number_emoji(n)} {text}"
        return f"{n}. {text}"

    def numbered_list_item(
        self, text: str, n: int, end: Optional[str] = None, use_emoji_numbers: bool = True,
    ):
        return self._append_with_end(
            self.as_numbered_list_item(text, n, use_emoji_numbers), end
        ).br()

    def numbered_list(self, items: Iterable[str], use_emoji_numbers: bool = True):
        for n, i in enumerate(items):
            self.numbered_list_item(text=i, n=n, use_emoji_numbers=use_emoji_numbers)
        return self

    # endregion
