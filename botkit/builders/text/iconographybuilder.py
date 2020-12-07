from typing import Optional

from botkit.builders.text.basetextbuilder import BaseTextBuilder
from botkit.builders.text.emoji import replace_emoji_aliases


class Iconography:
    ZERO_WIDTH_WHITESPACE = "\xad"
    EMOJI_NUMBERS = "0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣"
    EMOJI_SPACE = "	 	 "


class IconographyBuilder(BaseTextBuilder):
    def emoji_spc(self):
        """ Renders the horizontal width of an emoji as two `en` whitespace characters (U+2002) """
        self.parts.append(Iconography.EMOJI_SPACE)
        return self

    def zero_width_whitespace_1(self):
        self.parts.append(Iconography.ZERO_WIDTH_WHITESPACE)
        return self

    @classmethod
    def as_emojized(cls, alias: str):
        return replace_emoji_aliases(alias)

    def emojize(self, alias: str):
        self.parts.append(replace_emoji_aliases(alias))
        return self

    def dash_long(self, end: Optional[str] = " "):
        return self._append_with_end("—", end)

    @classmethod
    def as_number_emoji(cls, n: int) -> str:
        idx = str(n)
        result = []

        for char in idx:
            i = (int(char)) * 3
            result += Iconography.EMOJI_NUMBERS[i : i + 3]

        return "".join(result)

    def number_emoji(self, num: int):
        self.parts.append(self.as_number_emoji(num))
        return self
