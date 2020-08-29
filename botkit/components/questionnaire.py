from typing import Iterable, Any, Type, Union, Optional

from botkit.utils.sentinel import NotSet, Sentinel
from pydantic import BaseModel

from botkit.core.components import Component
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.views.botkit_context import BotkitContext


class Questionnaire(BaseModel):
    pass


class Slot(object):
    def __init__(self, query: str = None):
        self.query = query

    def __get__(self, instance: Any, objtype: Type):
        print("getting", instance, objtype)
        pass

    def __set__(self, instance, val):
        print("setting", instance, val)
        pass


class QuestionnaireComponent(Component):
    def __init__(self, name: str, slots: Iterable[Slot]):
        self.name = name
        self._slots = slots

    def register(self, routes: RouteBuilder):
        pass

    async def invoke(self, context: BotkitContext):
        for s in self._slots:
            pass
