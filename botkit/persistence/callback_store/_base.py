from uuid import UUID, uuid4
from typing import Literal, Union, Optional
from abc import abstractmethod
from haps import base
from abc import ABC

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from botkit.dispatching.types import CallbackActionType
from tgtypes.updatetype import UpdateType

TViewState = TypeVar("TViewState")


class CallbackActionContext(BaseModel, Generic[TViewState]):
    action: CallbackActionType
    state: TViewState
    triggered_by: Literal["button", "command"]
    created: datetime = Field(default_factory=datetime.utcnow)
    notification: Optional[str]
    show_alert: bool = False
    payload: Optional[Any] = None


TRIGGERED_BY_UPDATE_TYPES = {"button": UpdateType.callback_query, "command": UpdateType.message}


@base
class ICallbackStore(ABC):
    @abstractmethod
    def create_callback(self, context: CallbackActionContext) -> str:
        ...

    @abstractmethod
    def lookup_callback(self, id_: Union[str, UUID]) -> Optional[CallbackActionContext]:
        ...

    @abstractmethod
    def clear(self):
        ...

    @abstractmethod
    def force_sync(self):
        ...

    @abstractmethod
    def remove_outdated(self, days: int = 7):
        ...


def generate_id() -> str:
    return str(uuid4())
