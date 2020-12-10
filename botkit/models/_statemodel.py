from abc import ABC

from pydantic import BaseModel

from ._interfaces import IGatherer
from botkit.botkit_context import Context


class StateModel(BaseModel, IGatherer, ABC):
    @classmethod
    def create_from_context(cls, ctx: Context) -> "StateModel":
        pass
