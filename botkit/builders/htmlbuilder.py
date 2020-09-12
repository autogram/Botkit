from botkit.builders.text.telegram_entity_builder import TelegramEntityBuilder
from botkit.builders.text.typographybuilder import TypographyBuilder


class HtmlBuilder(TypographyBuilder, TelegramEntityBuilder):
    @property
    def is_dirty(self) -> bool:
        return bool(self.parts)
