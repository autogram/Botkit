from pyrogram import Emoji

from botkit.builders.htmlbuilder import HtmlBuilder
from botkit.views.views import TextView


class SuccessView(TextView[str]):
    def render_body(self, builder: HtmlBuilder) -> None:
        builder.text(Emoji.WHITE_HEAVY_CHECK_MARK).spc().text(self.state)
