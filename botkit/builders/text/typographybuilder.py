from typing import Optional

from botkit.builders.text.emoji import Emoji
from botkit.builders.text.htmltextbuilder import _HtmlTextBuilder
from botkit.builders.text.iconographybuilder import Iconography, IconographyBuilder
from botkit.builders.text.telegram_entity_builder import TelegramEntityBuilder


class TypographyBuilder(_HtmlTextBuilder, IconographyBuilder):
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

    def as_success(self, text):
        return "{} {}".format(Emoji.white_check_mark, text, hide_keyboard=True)

    def enforce_min_width(self, width: int):
        self.code_block(" " * width + Iconography.ZERO_WIDTH_WHITESPACE)

    def as_love(self, text):
        return "💖 {}".format(text, hide_keyboard=True)

    def as_failure(self, text):
        return "{} {}".format(Emoji.cross_heavy, text)

    def as_action_hint(self, text):
        return "💬 {}".format(text)

    def as_none_action(self, text):
        return "{} {}".format(Emoji.negative_squared_cross_mark, text)

    def as_cta(self, text):
        """ Call-to-action """
        return self.as_bold(self.as_action_hint(text))

    def cta(self, call_to_action: str, end: Optional[str] = "\n"):
        self._append_with_end(self.as_cta(call_to_action), end=end)
        return self
