from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, Union

from botkit.dispatching.callbackqueries.types import CallbackActionType
from botkit.future_tgtypes.update_field_extractor import UpdateFieldExtractor
from botkit.routing.types import TState
from botkit.views.sender_interface import IViewSender

TPayload = TypeVar("TPayload")


@dataclass
class BotkitContext(Generic[TState, TPayload], UpdateFieldExtractor):
    client: Union[IViewSender, Any]
    state: TState

    _action: Optional[CallbackActionType] = None
    _payload: Optional[TPayload] = None
