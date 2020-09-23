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
    - how to register views? autoregistration?
    - (how) can widgets be used by views?
    """

    def mutate(self):
        pass  # TODO
