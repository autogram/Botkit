from abc import ABC, abstractmethod

from botkit.builders import HtmlBuilder
from botkit.abstractions._named import INamed


class HtmlWidget(INamed, ABC):
    @abstractmethod
    def render_html(self, html: HtmlBuilder):
        pass
