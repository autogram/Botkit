from collections.abc import MutableMapping
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Iterator, Optional, TypeVar, Union

from botkit.dispatching.types import CallbackActionType
from botkit.future_tgtypes.update_field_extractor import UpdateFieldExtractor
from .rendered_messages import RenderedMessage
from ..future_tgtypes.chat_identity import ChatIdentity
from ..future_tgtypes.message_identity import MessageIdentity
from ..routing.types import TViewState
from ..routing.update_types.updatetype import UpdateType

TPayload = TypeVar("TPayload")


class _ScopedState(MutableMapping):
    def __init__(self):
        self._data = dict()

    def __setitem__(self, k, v) -> None:
        return self._data.__setitem__(k, v)

    def __delitem__(self, v) -> None:
        return self._data.__delitem__(v)

    def __getitem__(self, k) -> Any:
        return self._data.__getitem__(k)

    def __len__(self) -> int:
        return self._data.__len__()

    def __iter__(self) -> Iterator[Any]:
        return self._data.__iter__()


class ChatState(_ScopedState):
    def __init__(self, chat_identity: ChatIdentity):
        self.chat_identity = chat_identity
        super(ChatState, self).__init__()


class UserState(_ScopedState):
    def __init__(self):
        # TODO: implement descriptor
        super(UserState, self).__init__()


@dataclass
class Context(Generic[TViewState, TPayload], UpdateFieldExtractor):  # TODO: maybe `RouteContext`?
    # TODO: rename to `view_state`?
    # TODO: maybe this shouldn't even be part of the context but always be passed separately (because of reducers)?
    update_type: UpdateType
    view_state: TViewState

    action: Optional[CallbackActionType] = None
    payload: Optional[TPayload] = None

    message_state: Optional[Any] = None  # TODO: wtf
    user_state: Optional[UserState] = None
    chat_state: Optional[ChatState] = None

    # TODO: These should maybe not live on the context, but move to a dedicated `Pipeline(-specific)Context`
    rendered_message: RenderedMessage = None
    response_identity: MessageIdentity = None
