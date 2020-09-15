from abc import ABC, abstractmethod

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from botkit.views.botkit_context import Context


class ViewState(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def gather(cls, ctx: Context) -> "ViewState":
        ...
