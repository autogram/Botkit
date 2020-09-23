from contextlib import contextmanager
from typing import Any, Literal, Optional

from botkit.abstractions._named import INamed
from botkit.dispatching.types import CallbackActionType
from botkit.persistence.callback_store import CallbackActionContext, ICallbackStore
from botkit.routing.types import TViewState


class CallbackBuilder:
    _SEPARATOR = "##"

    def __init__(self, state: TViewState, callback_store: ICallbackStore):
        self.state = state
        self._callback_store = callback_store
        self._prefix_parts = []

    def create_callback(
        self,
        action_id: CallbackActionType,
        triggered_by: Literal["button", "command"],
        notification: Optional[str],
        show_alert: bool = False,
        payload: Optional[Any] = None,
    ) -> str:
        context = CallbackActionContext(
            action=self._format_action(action_id),
            state=self.state,
            triggered_by=triggered_by,
            notification=notification,
            show_alert=show_alert,
            payload=payload,
        )
        return self._callback_store.create_callback(context)

    def _format_action(self, action_id: CallbackActionType) -> str:
        action_id = self.__validate_action_id(action_id)
        if not self._prefix_parts:
            return action_id
        return f"{self._current_action_prefix}{self._SEPARATOR}{action_id}"

    def __validate_action_id(self, id_: str):
        if self._SEPARATOR in id_:
            raise ValueError(
                f"Sorry, but botkit uses the action substring '{self._SEPARATOR}' internally, so you cannot "
                f"use it."
            )
        return id_.strip().replace(" ", "")

    @property
    def _current_action_prefix(self):
        return self._SEPARATOR.join(self._prefix_parts)

    @contextmanager
    def scope(self, entity: INamed):
        self.push_scope(entity)
        yield
        self.pop_scope()

    def push_scope(self, entity: INamed):
        """
        Pushes an additional action prefix on the stack that all following builder methods will use until it is
        popped again using `pop_scope(entity)`.
        """
        self._prefix_parts.append(self.__validate_action_id(entity.unique_name))

    def pop_scope(self):
        """
        Removes the most recently added action prefix from the stack.
        """
        self._prefix_parts.pop()
