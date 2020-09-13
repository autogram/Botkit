from contextlib import contextmanager
from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    ContextManager,
    Generic,
    Iterable,
    Optional,
    TYPE_CHECKING,
    Type,
    TypeVar,
    Union,
    overload,
)
from uuid import UUID, uuid4

from pyrogram.filters import Filter, create
from pyrogram.handlers.handler import Handler
from pyrogram.types import CallbackQuery

from botkit.libraries.annotations import HandlerSignature
from botkit.routing.pipelines.collector import CollectorSignature
from botkit.routing.pipelines.execution_plan import (
    ExecutionPlan,
    RemoveTrigger,
    SendTarget,
    SendTo,
)
from botkit.routing.pipelines.gatherer import GathererSignature
from botkit.routing.pipelines.reducer import ReducerSignature
from botkit.routing.route import RouteDefinition
from botkit.routing.route_builder.publish_expression import PublishActionExpressionMixin
from botkit.routing.route_builder.route_collection import RouteCollection
from botkit.routing.route_builder.types import IExpressionWithCallMethod, TView
from botkit.routing.route_builder.webhook_action_expression import WebhookActionExpressionMixin
from botkit.routing.triggers import RouteTriggers
from botkit.routing.types import TViewState
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient
from botkit.views.base import InlineResultViewBase
from botkit.views.botkit_context import Context

if TYPE_CHECKING:
    from botkit.core.components import Component
else:
    Component = TypeVar("Component")

M = TypeVar("M")


class RouteExpression:
    def __init__(self, routes: RouteCollection, route: RouteDefinition):
        self._route_collection = routes
        self._route = route

    def and_fire(self, func: Callable[[TViewState], Union[None, Awaitable[None]]]):
        raise NotImplementedError()  # TODO: implement

    def and_transition_to(self, new_state: "StateRouteBuilder"):
        self._route.plan.set_next_state(new_state.state_guid)

    def and_exit_state(self):
        self._route.plan.set_next_state(None)

    def and_collect(self, func: CollectorSignature):
        self._route.plan.set_collector(func)
        return self

    def and_remove_trigger(
        self, strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me
    ) -> "RouteExpression":
        self._route.plan.set_remove_trigger(strategy)
        return self


class StateGenerationExpression(Generic[M]):
    def __init__(
        self, routes: RouteCollection, triggers: RouteTriggers, plan: ExecutionPlan,
    ):
        self._route_collection = routes
        self._triggers = triggers
        self._plan = plan

    def mutate(
        self: "ActionExpression", reducer: ReducerSignature
    ) -> "StateGenerationExpression[M]":
        self._plan.set_reducer(reducer)
        return StateGenerationExpression(self._route_collection, self._triggers, self._plan)

    def then_call(self, handler: HandlerSignature) -> RouteExpression:
        self._plan.set_handler(handler)
        route = RouteDefinition(self._triggers, self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def then_invoke(self, component: "Component") -> RouteExpression:
        self._plan.set_handling_component(component)
        route = RouteDefinition(self._triggers, self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def then_update(self, view_type) -> RouteExpression:
        self._plan.set_view(view_type, "update")
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def then_send(
        self, view_or_view_type, to: SendTarget = SendTo.same_chat, via: IClient = None
    ) -> RouteExpression:
        if via and not self._route_collection.current_client.is_user:
            raise ValueError(
                "Can only send a view `via` another bot when the client that this route belongs to is a "
                "userbot. A userbot and a regular bot together form a 'companion bot' relationship.",
                self._route_collection.current_client,
            )
        self._plan.set_view(view_or_view_type, "send").set_send_via(via).set_send_target(to)
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def remove_trigger(
        self, strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me
    ) -> "StateGenerationExpression[M]":
        self._plan.set_remove_trigger(strategy)
        return self


TViewBase = TypeVar("TViewBase", bound=InlineResultViewBase, covariant=True)


class ActionExpression(WebhookActionExpressionMixin, PublishActionExpressionMixin):
    def __init__(
        self,
        routes: RouteCollection,
        action: Union[int, str],
        condition: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None,
    ):
        super().__init__(routes, action, condition)
        self._route_collection = routes
        self._triggers = RouteTriggers(action=action, filters=None, condition=condition)
        self._plan = ExecutionPlan().add_update_types(UpdateType.callback_query)

    def call(self, handler: HandlerSignature) -> RouteExpression:
        self._plan.set_handler(handler)
        route = RouteDefinition(plan=self._plan, triggers=self._triggers)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def send_view(
        self, view_or_view_type, to: SendTarget = SendTo.same_chat, via: IClient = None,
    ):
        if via and not self._route_collection.current_client.is_user:
            raise ValueError(
                "Can only send a view `via` another bot when the client that this route belongs to is a "
                "userbot. A userbot and a regular bot together form a 'companion bot' relationship.",
                self._route_collection.current_client,
            )
        self._plan.set_view(view_or_view_type, "send").set_send_via(via).set_send_target(to)
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def mutate(
        self: "ActionExpression", reducer: ReducerSignature
    ) -> StateGenerationExpression[M]:
        # TODO: Allow multiple reducers
        self._plan.set_reducer(reducer)
        return StateGenerationExpression(self._route_collection, self._triggers, self._plan)

    def remove_trigger(
        self, strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me
    ) -> "ActionExpression":
        self._plan.set_remove_trigger(strategy)
        return self


class CommandExpression(WebhookActionExpressionMixin):
    def __init__(
        self,
        routes: RouteCollection,
        action: Union[int, str],
        condition: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None,
    ):
        super().__init__(routes, action, condition)
        self._route_collection = routes
        self._triggers = RouteTriggers(action=action, filters=None, condition=condition)

    def call(self, handler: HandlerSignature) -> RouteExpression:
        route = RouteDefinition(plan=ExecutionPlan().set_handler(handler), triggers=self._triggers)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def mutate(
        self: "ActionExpression", reducer: ReducerSignature
    ) -> StateGenerationExpression[M]:
        return StateGenerationExpression(
            self._route_collection, self._triggers, ExecutionPlan().set_reducer(reducer)
        )


class PlayGameExpression:
    def __init__(self, routes: RouteCollection, game_short_name: str):
        self._route_collection = routes
        self._triggers = RouteTriggers(
            filters=create(
                lambda _, __, cbq: cbq.game_short_name == game_short_name, "PlayGameFilter",
            ),
            action=None,
            condition=None,
        )

    def return_url(self, game_url: str) -> RouteExpression:
        async def return_website(client: IClient, callback_query: CallbackQuery):
            await callback_query.answer(url=game_url)

        plan = ExecutionPlan()
        plan.set_view()  # TODO probably shouldn't be a view..?
        route = RouteDefinition(plan=plan, triggers=self._triggers)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)


class ConditionsExpression(IExpressionWithCallMethod):
    def __init__(
        self,
        routes: RouteCollection,
        filters: Filter = None,
        condition: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None,
    ):
        self._route_collection = routes
        self._plan = ExecutionPlan()
        self._triggers = RouteTriggers(filters=filters, condition=condition, action=None)

    def call(self, handler: HandlerSignature) -> RouteExpression:
        self._plan.set_handler(handler)
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def send(
        self, view_or_view_type, to: SendTarget = SendTo.same_chat, via: IClient = None,
    ) -> RouteExpression:
        if via and not self._route_collection.current_client.is_user:
            raise ValueError(
                "Can only send a view `via` another bot when the client that this route belongs to is a "
                "userbot. A userbot and a regular bot together form a 'companion bot' relationship.",
                self._route_collection.current_client,
            )
        (
            self._plan.set_view(view_or_view_type, "send")
            .set_send_via(via)
            .set_send_target(to)
            .add_update_types(UpdateType.message)
        )
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def invoke(self, component: "Component"):
        raise NotImplemented()
        # component.register(self)
        # async def invoke_component(client: PyroRendererClientMixin, message: Message):
        #     component.
        #
        # plan = ExecutionPlan(return_website)
        # route = Route(plan=plan, triggers=self._triggers)
        # self._route_collection.add_for_current_client(route)
        # return RouteExpression(self._route_collection, route)

    def gather(self, state_generator: GathererSignature):
        self._plan.set_gatherer(state_generator).add_update_types(UpdateType.message)
        return StateGenerationExpression(self._route_collection, self._triggers, self._plan)

    def remove_trigger(
        self, strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me
    ) -> "ConditionsExpression":
        self._plan.set_remove_trigger(strategy)
        return self


@dataclass
class RouteBuilderContext:
    load_result: Optional[Any] = None
    """
    Contains the return value of a module's asynchronous `load()` method so that the synchronous `register` has
    access to data that should be retrieved from a coroutine.
    """


class RouteBuilder:
    def __init__(
        self,
        routes: RouteCollection = None,
        current_client: IClient = None,
        context: RouteBuilderContext = None,
    ):
        self._route_collection: RouteCollection = (RouteCollection() if routes is None else routes)
        self._current_client: Optional[IClient] = (
            current_client or self._route_collection.current_client or None
        )
        self.context = context or RouteBuilderContext()

    def use(self, client: IClient) -> "RouteBuilder":
        self._route_collection.current_client = client
        return self

    @contextmanager
    def using(self, client: IClient) -> ContextManager[None]:
        previous = self._route_collection.current_client
        self.use(client)
        yield
        self.use(previous)

    @contextmanager
    def only(self, filters: Filter):
        previous = self._route_collection.default_filters
        self._route_collection.default_filters = filters
        yield
        self._route_collection.default_filters = previous

    def add(self, route: RouteDefinition):
        self._route_collection.add_for_current_client(route)

    def on(
        self,
        filters: Optional[Filter],
        condition_func: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None,
    ) -> ConditionsExpression:
        return ConditionsExpression(
            self._route_collection, filters=filters, condition=condition_func,
        )

    # def on_trigger(
    #     self,
    #     command_definition: _ParsedCommandDefinition,
    #     extra_filters: Optional[Filter],
    #     condition_func: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None,
    # ):
    #     # TODO: implement
    #     # return CommandExpression(
    #     #     self._route_collection, command=command_definition, condition=condition_func
    #     # )
    #     raise NotImplemented

    def on_action(
        self,
        action: Union[str, int],
        condition_func: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None,
    ) -> ActionExpression:
        return ActionExpression(self._route_collection, action=action, condition=condition_func)

    def on_play_game(self, game_short_name: str) -> PlayGameExpression:
        return PlayGameExpression(self._route_collection, game_short_name=game_short_name)

    def always_call(self, handler: HandlerSignature) -> RouteExpression:
        return ConditionsExpression(self._route_collection).call(handler)

    def add_handler(self, handler: Handler):
        raise NotImplemented()
        # self._route_collection.add_for_current_client(Route())

    @overload
    def state_machine(self, states: Iterable[str]) -> Iterable["StateRouteBuilder"]:
        ...

    @overload
    def state_machine(self, num_states: int) -> Iterable["StateRouteBuilder"]:
        ...

    def state_machine(self, arg: Union[int, Iterable[str]]) -> Iterable["StateRouteBuilder"]:
        machine_guid = uuid4()
        if isinstance(arg, int):
            for i in range(arg):
                yield StateRouteBuilder(machine_guid, i, self._route_collection)
        else:
            for i, name in enumerate(arg):
                yield StateRouteBuilder(machine_guid, i, self._route_collection, name=name)


class StateRouteBuilder(RouteBuilder):
    def __init__(self, machine_guid: UUID, index: int, routes: RouteCollection, name: str = None):
        super().__init__(routes)
        self.state_guid = uuid4()
        self.machine_guid = machine_guid
        self.index = index
        self.name = name
        self._route_collection = routes
