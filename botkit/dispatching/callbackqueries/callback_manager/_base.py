from pydantic import BaseModel
from pydantic.fields import Field
from uuid import UUID, uuid4
from typing import Union, Optional, TypeVar, Generic, Any
from abc import ABCMeta, abstractmethod
from haps import base
from datetime import datetime
from abc import ABC

from botkit.dispatching.callbackqueries.types import CallbackActionType

TModel = TypeVar("TModel")


class CallbackActionContext(BaseModel, Generic[TModel]):
    action: CallbackActionType
    state: TModel
    created: datetime = Field(default_factory=datetime.utcnow)
    notification: Optional[str]
    show_alert: bool = False
    payload: Optional[Any] = None


@base
class ICallbackManager(ABC):
    @abstractmethod
    def create_callback(self, context: CallbackActionContext) -> str:
        ...

    @abstractmethod
    def lookup_callback(self, id_: Union[str, UUID]) -> Optional[CallbackActionContext]:
        ...

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def force_sync(self):
        pass


def generate_id() -> str:
    return str(uuid4())
