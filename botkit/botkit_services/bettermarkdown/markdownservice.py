from abc import abstractmethod, ABCMeta

from haps import base, egg, Inject

from botkit.botkit_services.bettermarkdown.aliases import INLINE
from botkit.botkit_services.bettermarkdown.bettermarkdown import Renderer
from botkit.botkit_services.bettermarkdown.bettermarkdownlexer import BetterMarkdownLexer
from botkit.botkit_services.options.base import ToggleOption, IOptionStore


@base
class IMarkdownService(ABC):
    MARKDOWN_OPTION = ToggleOption('markdown', "Markdown", on_by_default=True, aliases=['md'])

    @abstractmethod
    def parse_html(self, text: str) -> str: pass


@egg
class MarkdownService(IMarkdownService):
    option_store: IOptionStore = Inject()

    def parse_html(self, text: str) -> str:
        if not self.option_store.get_value(self.MARKDOWN_OPTION):
            return text

        # renderer = TelegramRenderer(escape=True, hard_wrap=True)
        renderer = Renderer(escape=True, hard_wrap=True)
        lexer = BetterMarkdownLexer(renderer, aliases=INLINE)
        markdown = Markdown(inline=lexer)
        return markdown(text).strip()


if __name__ == '__main__':
    s = MarkdownService()
    print(s.parse_html('man...'))
