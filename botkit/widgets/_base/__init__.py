from abc import ABC
from typing import Generic, TypeVar

from botkit.routing.types import TViewState
from botkit.widgets._base.html_widget import HtmlWidget
from botkit.widgets._base.menu_widget import MenuWidget
from botkit.widgets._base.meta_widget import MetaWidget

TWidgetState = TypeVar("TWidgetState")


class Widget(Generic[TViewState, TWidgetState], HtmlWidget, MenuWidget, MetaWidget, ABC):
    """
    ## Invariants:
    - no load/unload (nothing async)

    ## Problems:
    If widgets get associated by doing e.g. `html.add(MyNewWidget())`, they won't be routable anymore.
    --> how to register views?
    """

    def mutate(self):
        pass  # TODO
