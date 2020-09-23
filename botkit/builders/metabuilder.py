from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botkit.widgets import MetaWidget


class MetaBuilder:
    def __init__(self):
        self.description = None
        self.title = None

    @property
    def is_dirty(self) -> bool:
        return self.description or self.title

    def add(self, widget: "MetaWidget") -> "MetaBuilder":
        widget.render_meta(self)
        return self
