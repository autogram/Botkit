from botkit.builders import CallbackBuilder, HtmlBuilder, MenuBuilder, MetaBuilder
from botkit.views.rendered_messages import RenderedMessage, RenderedTextMessage


class ViewBuilder:
    html: HtmlBuilder
    menu: MenuBuilder
    meta: MetaBuilder

    def __init__(self, callback_builder: CallbackBuilder):
        self.html = HtmlBuilder(callback_builder)
        self.menu = MenuBuilder(callback_builder)
        self.meta = MetaBuilder()

    def add(self, widget: "Widget"):
        self.html.add(widget)
        self.menu.add(widget)
        self.meta.add(widget)
        widget.render_html(self.html)

    @property
    def is_dirty(self) -> bool:
        return any((x.is_dirty for x in [self.html, self.menu, self.meta]))

    def render(self) -> RenderedMessage:
        # TODO: implement the other message types aswell
        html_text = self.html.render_html()
        rendered_menu = self.menu.render()
        return RenderedTextMessage(
            text=html_text,
            inline_buttons=rendered_menu,
            title=self.meta.title,
            description=self.meta.description,
        )
