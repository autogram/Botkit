from typing import Any, Callable, List, NoReturn, TYPE_CHECKING, Union
from injector import inject

from botkit.builders import CallbackBuilder
from botkit.builders.text.basetextbuilder import TState
from botkit.builders.text.htmltextbuilder import _HtmlTextBuilder
from botkit.builders.text.telegram_entity_builder import EntityBuilder
from botkit.builders.text.typographybuilder import TypographyBuilder

if TYPE_CHECKING:
    from botkit.widgets import HtmlWidget

"""
# More ideas:

- `html.desc("https://blabla", "")`  -->  ""
"""


class HtmlBuilder(TypographyBuilder, EntityBuilder):
    @inject
    def __init__(self, callback_builder: CallbackBuilder = None):
        super().__init__(callback_builder)

    def add(self, widget: "HtmlWidget") -> "HtmlBuilder":
        with self.callback_builder.scope(widget):
            widget.render_html(self)
        return self

    s = _HtmlTextBuilder.strike
    u = _HtmlTextBuilder.underline
    i = _HtmlTextBuilder.italic
    b = _HtmlTextBuilder.bold
    lin = _HtmlTextBuilder.link


HtmlRenderer = Callable[[TState, HtmlBuilder], Union[NoReturn, Any]]


if __name__ == "__main__":
    from botkit.widgets import HtmlWidget

    class ListView(HtmlWidget):
        def __init__(self, items: List[Any]):
            self.items = items

        unique_name = "my_list_view"

        def render_html(self, html: HtmlBuilder):
            html.list(self.items)

    html = HtmlBuilder(None)

    html.add(ListView(["henlo", "fren", "waddup"]))

    html("I am ").b("testing")

    print(html.render_html())
