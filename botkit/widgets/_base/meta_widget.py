from abc import ABC, abstractmethod

from botkit.abstractions._named import INamed
from botkit.builders import MetaBuilder


class MetaWidget(INamed, ABC):
    @abstractmethod
    def render_meta(self, meta: MetaBuilder):
        pass
