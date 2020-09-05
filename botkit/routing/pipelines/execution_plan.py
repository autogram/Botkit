import inspect
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional, Set, Tuple, Type, Union
from uuid import UUID

from typing_extensions import Literal

from botkit.core.components import Component
from botkit.libraries.annotations import HandlerSignature
from botkit.routing.pipelines.gatherer import (
    GathererSignature,
    GathererSignatureExamplesStr,
)
from botkit.routing.pipelines.reducer import (
    ReducerSignature,
    ReducerSignatureExamplesStr,
)
from botkit.routing.route_builder.types import TView
from botkit.routing.update_types.update_type_inference import infer_update_types
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient
from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import Context
from botkit.views.functional_views import ViewRenderFuncSignature
from botkit.views.views import MessageViewBase


class SendTo(Enum):
    self = auto()
    same_chat = auto()
    same_chat_quote = auto()
    same_chat_quote_replied_to = auto()
    same_chat_quote_original_replied_to = auto()
    user_in_private = auto()


ChatTarget = Union[SendTo, int, str]

SendTargetFuncSignature = Callable[
    [Context], Union[ChatTarget, Tuple[ChatTarget, Optional[int]]]
]
SendTargetFuncSignatureExamplesStr = """
def _(ctx: Context) -> SendTo: ...
def _(ctx: Context) -> Union[int, str]: ...
def _(ctx: Context) -> Tuple[SendTo, None]: ...
def _(ctx: Context) -> Tuple[SendTo, int]: ...
"""
SendTarget = Union[ChatTarget, SendTargetFuncSignature]

ViewCommandLiteral = Literal["send", "update"]


@dataclass
class ViewParameters:
    command: ViewCommandLiteral
    view: Union[Type[MessageViewBase], MessageViewBase, ViewRenderFuncSignature]
    send_via: Optional[IClient] = None
    send_target: Optional[SendTarget] = SendTo.same_chat


class RemoveTrigger(Enum):
    only_for_me = "only_me"
    aggressively = "aggressively"


class ExecutionPlan:
    def __init__(self) -> None:
        self._gatherer: Optional[TypedCallable[GathererSignature]] = None
        self._reducer: Optional[TypedCallable[ReducerSignature]] = None
        self._handler: Optional[TypedCallable[HandlerSignature]] = None
        self._handling_component: Optional[Component] = None
        self._view: Optional[ViewParameters] = None
        self._update_types: Set[UpdateType] = set()
        self._remove_trigger_setting: Optional[RemoveTrigger] = None
        self._state_transition: Optional[UUID] = None  # TODO: implement

    def set_gatherer(
        self, state_generator: Optional[GathererSignature]
    ) -> "ExecutionPlan":
        if self._reducer:
            raise ValueError("Route cannot have both a gatherer and a reduce step.")

        if state_generator is None:
            return self

        # TODO: test
        # if inspect.isclass(state_generator):
        #     gatherer = TypedCallable(func=lambda: state_generator())
        # else:
        gatherer = TypedCallable(func=state_generator)

        if gatherer.num_non_optional_params > 1:
            raise ValueError(
                f"Reducer must be a callable with one of the following signatures:\n{GathererSignatureExamplesStr}"
            )

        self._gatherer = gatherer
        return self

    def set_reducer(self, mutation_func: Optional[ReducerSignature]) -> "ExecutionPlan":
        if self._gatherer:
            raise ValueError("Route cannot have both a handler and a gatherer step.")

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

    def set_handler(self, handler: HandlerSignature) -> "ExecutionPlan":
        self._handler = TypedCallable(func=handler)
        inferred_update_types = infer_update_types(self._handler)

        if not inferred_update_types:
            raise ValueError(
                f"Could not infer update types from the callback {handler}."
            )

        self._set_update_types_exclusive(
            inferred_update_types,
            lambda invalid: ValueError(
                f"The given handler signature {self._handler} is not compatible with the "
                f"other actions added to this execution plan, namely {invalid}."
            ),
        )
        return self

    def set_handling_component(self, component: Component) -> "ExecutionPlan":
        self._handling_component = component
        return self

    def set_next_state(self, next_state_guid: Optional[UUID]) -> "ExecutionPlan":
        self._state_transition = next_state_guid
        return self

    def set_view(self, view: TView, command: ViewCommandLiteral) -> "ExecutionPlan":
        """
        If `send_via` is present, then the executing client must be a userbot. This is checked when using
        the `RouteBuilder`.
        """
        if not self._update_types:
            self.add_update_type(UpdateType.message)
        if self._view is not None:
            raise ValueError(
                "View is already set. Not sure what to do with this, most likely a bug. Contact @JosXa."
            )

        if inspect.isawaitable(view):
            raise ValueError("A view function must not be awaitable.")

        if command == "send":
            # TODO: Allow specifying the send target
            self._view = ViewParameters(
                command=command, view=view, send_target=SendTo.same_chat
            )
        elif command == "update":
            self._view = ViewParameters(command=command, view=view)
        else:
            raise ValueError(f"Unknown view command: '{command}'")

        return self

    def set_send_via(self, send_via: IClient) -> "ExecutionPlan":
        if send_via is None:
            self._view.send_via = None
            return self

        if not self._view:
            raise ValueError("Please specify the view to be sent first.")

        if not send_via.is_bot:
            raise ValueError(
                "Sending a message `via` is only possible with regular bots, not with userbots.",
                send_via,
            )

        if self._view.command == "update":
            raise ValueError(
                "Cannot *update* a view `via` another bot. This is only possible when *sending* a new view."
            )

        self._view.send_via = send_via
        return self

    def set_send_target(self, send_target: SendTarget) -> "ExecutionPlan":
        if not self._view:
            raise ValueError("A view should be set before specifying a send target.")

        if self._view.command == "update":
            raise NotImplementedError(
                "I am not sure what should happen when trying to *update* an existing view with "
                "a specific `send_target` (which might be different from that of the existing message). "
                "If you have a valid use case for this, please open a GitHub issue!"
            )

        self._view.send_target = send_target
        return self

    def add_update_type(self, update_type: UpdateType) -> "ExecutionPlan":
        self._update_types.add(update_type)
        return self

    def _set_update_types_exclusive(
        self, desired_types: Set[UpdateType], error_cb: Callable[[Set[str]], Exception]
    ) -> None:
        if invalid_elems := {
            t.name for t in self._update_types if t not in desired_types
        }:
            raise error_cb(invalid_elems)
        self._update_types = desired_types

    def set_remove_trigger(self, remove_trigger: Union[RemoveTrigger, bool, None]):
        if isinstance(remove_trigger, bool):
            self._remove_trigger_setting = (
                RemoveTrigger.only_for_me if remove_trigger else None
            )
        else:
            # enum or None
            self._remove_trigger_setting = remove_trigger
        return self
