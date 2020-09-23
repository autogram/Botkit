import inspect
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Iterable, Optional, Set, Tuple, Type, Union, cast
from uuid import UUID

from boltons.iterutils import is_collection
from pydantic import validator
from typing_extensions import Literal

from botkit.core.components import Component
from botkit.libraries.annotations import HandlerSignature
from botkit.models import IGatherer
from botkit.routing.pipelines.collector import CollectorSignature
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


# region Send targets


class SendTo(Enum):
    self = auto()
    same_chat = auto()
    same_chat_quote = auto()
    same_chat_quote_replied_to = auto()
    same_chat_quote_original_replied_to = auto()
    user_in_private = auto()


ChatTarget = Union[SendTo, int, str]

SendTargetFuncSignature = Callable[[Context], Union[ChatTarget, Tuple[ChatTarget, Optional[int]]]]
SendTargetFuncSignatureExamplesStr = """
def _(ctx: Context) -> SendTo: ...
def _(ctx: Context) -> Union[int, str]: ...
def _(ctx: Context) -> Tuple[SendTo, None]: ...
def _(ctx: Context) -> Tuple[SendTo, int]: ...
"""
SendTarget = Union[ChatTarget, SendTargetFuncSignature]

# endregion

# region Update targets


class UpdateAt(Enum):
    this = auto()
    replied_to = auto()


# TODO
EditTargetExamplesStr = """
"""
SendTarget = Union[ChatTarget, SendTargetFuncSignature]

# endregion


ViewCommandLiteral = Literal["send", "update"]


@dataclass
class ViewParameters:
    command: ViewCommandLiteral

    # TODO: This should not be a part of this class!
    view: Union[Type[MessageViewBase], MessageViewBase, ViewRenderFuncSignature]

    send_from: Optional[IClient] = None
    send_via_bot: Optional[IClient] = None

    # TODO: Make this a list of items?
    send_target: Optional[SendTarget] = SendTo.same_chat

    @validator("send_target")
    def validate_send_target(cls, _):
        if cls.command == "update":
            raise NotImplementedError(
                "I am not sure what should happen when trying to *update* an existing view with "
                "a specific `send_target` (which might be different from that of the existing message). "
                "If you have a valid use case for this, please open a GitHub issue!"
            )


class RemoveTrigger(Enum):
    only_for_me = "only_me"
    aggressively = "aggressively"


@dataclass
class RemoveTriggerParameters:
    strategy: RemoveTrigger
    always: bool
    early: bool


class ExecutionPlan:
    def __init__(self, client: IClient) -> None:
        self._client_type: Literal["user", "bot"] = cast(
            Literal["user", "bot"], "bot" if client.is_bot else "user"
        )
        self._gatherer: Optional[TypedCallable[GathererSignature]] = None
        self._reducer: Optional[TypedCallable[ReducerSignature]] = None
        self._handler: Optional[TypedCallable[HandlerSignature]] = None
        self._handling_component: Optional[Component] = None
        self._view: Optional[ViewParameters] = None
        self._update_types: Set[UpdateType] = set()
        self._remove_trigger_params: Optional[RemoveTriggerParameters] = None
        self._state_transition: Optional[UUID] = None  # TODO: implement
        self._collector: Optional[TypedCallable[CollectorSignature]] = None

    def set_gatherer(self, state_generator: Optional[GathererSignature]) -> "ExecutionPlan":
        if self._reducer:
            raise ValueError("Route cannot have both a gatherer after a reduce step.")

        if state_generator is None:
            return self

        # TODO: test
        # if inspect.isclass(state_generator):
        #     gatherer = TypedCallable(step_func=lambda: state_generator())
        # else:

        if inspect.isclass(state_generator) and issubclass(state_generator, IGatherer):
            state_generator = state_generator.create_from_context

        gatherer = TypedCallable(func=state_generator)

        if gatherer.num_non_optional_params > 1:
            raise ValueError(
                f"Reducer must be a callable with one of the following signatures:\n{GathererSignatureExamplesStr}"
            )

        self._gatherer = gatherer
        return self

    def set_reducer(self, mutation_func: Optional[ReducerSignature]) -> "ExecutionPlan":
        # TODO: allow multiple reducers

        # if (
        #     UpdateType.message not in self._update_types
        #     and UpdateType.callback_query not in self._update_types
        # ):
        #     raise ValueError("Route")
        #
        # self._set_update_types_exclusive(
        #     {UpdateType.callback_query},
        #     lambda invalid_elems: NotImplementedError(
        #         "Reducers / view_state mutations can only be added to callback "
        #         f"queries (for now), but the plan is to use {invalid_elems}."
        #     ),
        # )

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

    def set_collector(self, collector_func: Optional[CollectorSignature]) -> "ExecutionPlan":
        if collector_func is None:
            self._collector = None
            return self

        collector = TypedCallable(func=collector_func)

        if collector.num_parameters != 1:
            raise ValueError(
                f"Collector must be a function or coroutine with a single parameter `Context`."
            )

        self._collector = collector
        return self

    def set_handler(self, handler: HandlerSignature) -> "ExecutionPlan":
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

    def set_handling_component(
        self, component: Union[Component, Type[Component]]
    ) -> "ExecutionPlan":
        if self._handling_component:
            raise ValueError("There can only be one component in a given route.")

        if inspect.isclass(component):
            try:
                component = component()
            except:
                raise ValueError(
                    f"Component {component} is a class, but does not have a parameterless initializer."
                )

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
            self.add_update_types(UpdateType.message)
        if self._view is not None:
            raise ValueError(
                "View is already set. Not sure what to do with this, most likely a bug. Contact @JosXa."
            )

        if inspect.isawaitable(view):
            raise ValueError("A view function must not be awaitable.")

        if command == "send":
            # TODO: Allow specifying the send target
            self._view = ViewParameters(command=command, view=view, send_target=SendTo.same_chat)
        elif command == "update":
            self._view = ViewParameters(command=command, view=view)
        else:
            raise ValueError(f"Unknown view command: '{command}'")

        return self

    def set_from_and_via(
        self, from_client: IClient = None, send_via_bot: IClient = None
    ) -> "ExecutionPlan":
        if not from_client and not send_via_bot:
            self._view.send_from = None
            self._view.send_via_bot = None
            return self

        if not self._view:
            raise ValueError("Please specify the view to be sent first.")

        if send_via_bot and self._view.command == "update":
            raise ValueError(
                "Cannot *update* a view `via` another bot. This is only possible when *sending* a new view."
            )

        if not send_via_bot.is_bot:
            raise ValueError(
                "Sending a message `via` is only possible with regular bots, not with user clients.",
                send_via_bot,
            )

        if from_client and send_via_bot:
            if from_client.is_bot:
                raise ValueError(
                    "Sending a message `via` a bot is only possible when `send_from` is a user client.",
                    from_client,
                )
            self._view.send_from = from_client
            self._view.send_via_bot = send_via_bot
            return self

        if from_client:  # and not send_via_bot
            self._view.send_from = from_client
            return self

        if send_via_bot:  # and not send_from
            if self._client_type != "user":
                raise ValueError(
                    "Sending a message `via` a bot is only possible when the current client is a user client.",
                    send_via_bot,
                )
            self._view.send_via_bot = send_via_bot
            return self

        raise NotImplementedError("some condition is missing here...")

    def set_send_target(self, send_target: SendTarget) -> "ExecutionPlan":
        if not self._view:
            raise ValueError("A view should be set before specifying a send target.")

        self._view.send_target = send_target
        return self

    def add_update_types(
        self, update_types: Union[UpdateType, Iterable[UpdateType]]
    ) -> "ExecutionPlan":
        if is_collection(update_types):
            for udt in update_types:
                self._update_types.add(udt)
        else:
            self._update_types.add(update_types)
        return self

    def _set_update_types_exclusive(
        self, desired_types: Set[UpdateType], error_cb: Callable[[Set[str]], Exception]
    ) -> None:
        # TODO: This is a hotfix (1)
        if UpdateType.start_command in self._update_types:
            desired_types.add(UpdateType.start_command)

        if invalid_elems := {t.name for t in self._update_types if t not in desired_types}:
            raise error_cb(invalid_elems)
        self._update_types = desired_types

    def set_remove_trigger(
        self,
        strategy: Union[RemoveTrigger, bool, None],
        always: bool = False,
        early: bool = False,
    ):
        if isinstance(strategy, bool):
            self._remove_trigger_params = RemoveTriggerParameters(
                strategy=RemoveTrigger.only_for_me if strategy else None,
                always=always,
                early=early,
            )
        else:
            # enum or None
            self._remove_trigger_params = RemoveTriggerParameters(
                strategy=strategy, always=always, early=early
            )
        return self
