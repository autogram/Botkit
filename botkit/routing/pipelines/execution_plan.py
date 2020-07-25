from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Set, Type, Union
from uuid import UUID

from typing_extensions import Literal

from botkit.routing.pipelines.gatherer import GathererSignature, GathererSignatureExamplesStr
from botkit.routing.pipelines.reducer import ReducerSignature, ReducerSignatureExamplesStr
from botkit.routing.route_builder.types import TView
from botkit.routing.pipelines.callbacks import CallbackSignature
from botkit.routing.update_types.update_type_inference import infer_update_types
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.typed_callable import TypedCallable
from botkit.views.views import MessageViewBase


class SendTarget(Enum):
    to_same_chat = 1
    to_same_chat_quote = 2
    to_same_chat_quote_replied_to = 3
    to_user_in_private = 4
    to_specific_chat = 5  # TODO: implement
    # edit_outgoing = x  <-- Nope. I think this should be handled by quick actions


ViewCommandLiteral = Literal["send", "update"]


@dataclass
class ViewParameters:
    command: ViewCommandLiteral
    view: Union[Type[MessageViewBase], MessageViewBase]
    send_target: Optional[SendTarget] = None


# TODO: refactor to have only `add_step(Factory)`! Each `set_*` should add a factory type.
class ExecutionPlan:
    def __init__(self) -> None:
        self._gatherer: Optional[TypedCallable[GathererSignature]] = None
        self._reducer: Optional[TypedCallable[ReducerSignature]] = None
        self._handler: Optional[TypedCallable[CallbackSignature]] = None
        self._view: Optional[ViewParameters] = None
        self._state_transition: Optional[UUID] = None  # TODO: implement
        self._update_types: Set[UpdateType] = set()

    def set_gatherer(self, state_generator: Optional[GathererSignature]) -> "ExecutionPlan":
        if self._reducer:
            raise ValueError("Route cannot have both a gatherer and a reduce step.")

        if state_generator is None:
            return self

        gatherer = TypedCallable(func=state_generator)

        if gatherer.num_non_optional_params > 1:
            raise ValueError(
                f"Reducer must be a callable with one of the following signatures:\n{GathererSignatureExamplesStr}"
            )

        self._gatherer = gatherer
        return self

    def set_reducer(self, mutation_func: Optional[ReducerSignature]) -> "ExecutionPlan":
        if self._gatherer:
            raise ValueError("Route cannot have both a reducer and a gatherer step.")

        self._set_update_types_exclusive(
            {UpdateType.callback_query},
            lambda invalid_elems: NotImplementedError(
                "Reducers / state mutations can only be added to callback "
                f"queries (for now), but the plan is to use {invalid_elems}."
            ),
        )

        if mutation_func is None:
            self._reducer = None
            return self

        handler = TypedCallable(func=mutation_func)

        if handler.num_parameters not in (1, 2):
            raise ValueError(
                f"Reducer must be a callable with one of the following signatures:\n{ReducerSignatureExamplesStr}"
            )

        self._reducer = handler
        return self

    def set_handler(self, handler: CallbackSignature) -> "ExecutionPlan":
        self._handler = TypedCallable(func=handler)
        inferred_update_types = infer_update_types(self._handler)

        if not inferred_update_types:
            raise ValueError(f"Could not infer update types from the callback {handler}.")

        self._set_update_types_exclusive(
            inferred_update_types,
            lambda invalid: ValueError(
                f"The given handler signature {self._handler} is not compatible with the "
                f"other actions added to this execution plan, namely {invalid}."
            ),
        )
        return self

    def set_next_state(self, next_state_guid: Optional[UUID]) -> "ExecutionPlan":
        self._state_transition = next_state_guid
        return self

    def set_view(self, view: TView, command: ViewCommandLiteral) -> "ExecutionPlan":
        if self._view is not None:
            raise ValueError("View is already set. Not sure what to do with this, most likely a bug. Contact @JosXa.")

        if command == "send":
            # Set a default send target
            self._view = ViewParameters(command=command, view=view, send_target=SendTarget.to_same_chat)
        elif command == "update":
            self._view = ViewParameters(command=command, view=view)
        else:
            raise ValueError(f"Unknown view command: '{command}'")

        return self

    def set_send_target(self, send_target: SendTarget) -> "ExecutionPlan":
        # TODO: use
        if not self._view:
            raise ValueError("A view should be set before choosing a send target.")
        self._view.send_target = send_target
        return self

    def add_update_type(self, update_type: UpdateType) -> "ExecutionPlan":
        self._update_types.add(update_type)
        return self

    def _set_update_types_exclusive(
        self, types: Set[UpdateType], error_cb: Callable[[Set[UpdateType]], Exception]
    ) -> None:
        assert not (UpdateType.callback_query in self._update_types and UpdateType.message in types)
        if invalid_elems := {t for t in self._update_types if t not in types}:
            raise error_cb(invalid_elems)
        self._update_types = types
