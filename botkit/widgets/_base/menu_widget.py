from abc import ABC, abstractmethod

from botkit.builders import MenuBuilder


class MenuWidget(ABC):
    @abstractmethod
    def render_menu(self, menu: MenuBuilder):
        pass
