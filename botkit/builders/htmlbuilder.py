from typing import Any, Callable, NoReturn, TYPE_CHECKING, Union

from botkit.builders.text.basetextbuilder import TState
from botkit.builders.text.telegram_entity_builder import NavigationBuilder
from botkit.builders.text.typographybuilder import TypographyBuilder

if TYPE_CHECKING:
    from botkit.widgets import HtmlWidget


class HtmlBuilder(TypographyBuilder, NavigationBuilder):
    @property
    def is_dirty(self) -> bool:
        return bool(self.parts)

    def add(self, widget: "HtmlWidget") -> "HtmlBuilder":
        with self.callback_builder.scope(widget):
            widget.render_html(self)
        return self


HtmlRenderer = Callable[[TState, HtmlBuilder], Union[NoReturn, Any]]
