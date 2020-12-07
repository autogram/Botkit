from typing import (
    Awaitable,
    Callable,
    Generic,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    Union,
)

from pyrogram.filters import Filter, create
from pyrogram.types import CallbackQuery

from botkit.agnostic.annotations import HandlerSignature
from botkit.routing.pipelines.collector import CollectorSignature
from botkit.routing.pipelines.executionplan import (
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
from botkit.routing.route_builder.expressions._base import IExpressionWithCallMethod

from botkit.routing.route_builder.webhook_action_expression import WebhookActionExpressionMixin
from botkit.routing.triggers import RouteTriggers
from botkit.routing.types import TViewState
from tgtypes.updatetype import UpdateType
from botkit.clients.client import IClient
from botkit.views.base import InlineResultViewBase

if TYPE_CHECKING:
    from botkit.core.components import Component
    from botkit.routing.route_builder.state_route_builder import StateRouteBuilder
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
        self, strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me,
    ) -> "RouteExpression":
        self._route.plan.set_remove_trigger(strategy, always=False, early=False)
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
        self,
        view,
        to: SendTarget = SendTo.same_chat,
        from_client: IClient = None,
        via_bot: IClient = None,
    ) -> RouteExpression:
        (
            self._plan.set_view(view, "send")
            .set_from_and_via(from_client, via_bot)
            .set_send_target(to)
        )
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def remove_trigger(
        self,
        strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me,
        always: bool = False,
    ) -> "StateGenerationExpression[M]":
        self._plan.set_remove_trigger(strategy, always=always, early=True)
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
        self._plan = ExecutionPlan(self._route_collection.current_client).add_update_types(
            {UpdateType.callback_query, UpdateType.start_command}
        )

    def call(self, handler: HandlerSignature) -> RouteExpression:
        self._plan.set_handler(handler)
        route = RouteDefinition(plan=self._plan, triggers=self._triggers)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def send_view(
        self,
        view_or_view_type,
        to: SendTarget = SendTo.same_chat,
        from_client: IClient = None,
        via_bot: IClient = None,
    ):
        self._plan.set_view(view_or_view_type, "send").set_from_and_via(
            from_client=from_client, send_via_bot=via_bot
        ).set_send_target(to)
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
        self,
        strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me,
        always: bool = False,
    ) -> "ActionExpression":
        self._plan.set_remove_trigger(strategy, always=always, early=True)
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
        route = RouteDefinition(
            plan=ExecutionPlan(self._route_collection.current_client).set_handler(handler),
            triggers=self._triggers,
        )
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def mutate(
        self: "ActionExpression", reducer: ReducerSignature
    ) -> StateGenerationExpression[M]:
        return StateGenerationExpression(
            self._route_collection,
            self._triggers,
            ExecutionPlan(self._route_collection.current_client).set_reducer(reducer),
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

        plan = ExecutionPlan(self._route_collection.current_client)
        plan.set_handler(return_website)
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
        self._plan = ExecutionPlan(self._route_collection.current_client)
        self._triggers = RouteTriggers(filters=filters, condition=condition, action=None)

    def call_with_traits(self, handler: Callable) -> RouteExpression:
        self._plan.set_handler(handler)
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def call(self, handler: HandlerSignature) -> RouteExpression:
        self._plan.set_handler(handler)
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def send(
        self,
        view_or_view_type,
        to: SendTarget = SendTo.same_chat,
        from_client: IClient = None,
        via_bot: IClient = None,
    ) -> RouteExpression:
        (
            self._plan.set_view(view_or_view_type, "send")
            .set_from_and_via(from_client, via_bot)
            .set_send_target(to)
            .add_update_types(UpdateType.message)
        )
        route = RouteDefinition(triggers=self._triggers, plan=self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def invoke(self, component: "Component"):
        self._plan.set_handling_component(component)
        route = RouteDefinition(self._triggers, self._plan)
        self._route_collection.add_for_current_client(route)
        return RouteExpression(self._route_collection, route)

    def gather(self, state_generator: GathererSignature):
        self._plan.set_gatherer(state_generator).add_update_types(UpdateType.message)
        return StateGenerationExpression(self._route_collection, self._triggers, self._plan)

    def remove_trigger(
        self,
        strategy: Union[RemoveTrigger, bool, None] = RemoveTrigger.only_for_me,
        always: bool = False,
    ) -> "ConditionsExpression":
        self._plan.set_remove_trigger(strategy, always=always, early=True)
        return self
