from urllib.parse import urlencode

from botkit.builders.text.typographybuilder import TypographyBuilder


class HtmlBuilder(TypographyBuilder):
    @classmethod
    def as_prompt(cls, text) -> "str":
        text = urlencode(text)
        return f"https://telegram.me/share/url?url={text}"
