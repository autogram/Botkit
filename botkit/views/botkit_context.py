from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, Union

from botkit.dispatching.callbackqueries.types import CallbackActionType
from botkit.future_tgtypes.update_field_extractor import UpdateFieldExtractor
from .rendered_messages import RenderedMessage
from .sender_interface import IViewSender
from ..routing.types import TState

TPayload = TypeVar("TPayload")


class IContextStore:
    """
    TODO: These are experiments. What is needed?
    - per chat global
    - per user global
    - per chat and module
    - per user and module
    - associated to message (is this equivalent to "per view", i.e. `view_state`?)
    """

    @property
    @abstractmethod
    def chat(self):
        ...


@dataclass
class Context(Generic[TState, TPayload], UpdateFieldExtractor):
    # store: IContextStore = None

    # TODO: rename to `view_state`?
    # TODO: maybe this shouldn't even be part of the context ubt always be passed separately (because of reducers)?
    state: TState

    client: Union[IViewSender, Any]
    action: Optional[CallbackActionType] = None
    payload: Optional[TPayload] = None

    # TODO: It might or might not make sense to have this here. It may be removed in the future in favor of
    # simple argument passing inside the pipelines.
    rendered_message: RenderedMessage = None
