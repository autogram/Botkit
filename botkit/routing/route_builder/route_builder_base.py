from contextlib import contextmanager
from typing import (
    Awaitable,
    Callable,
    ContextManager,
    Optional,
    Union,
)

from pyrogram.filters import Filter
from pyrogram.handlers.handler import Handler

from botkit.agnostic import HandlerSignature
from botkit.routing.route import RouteDefinition
from botkit.routing.route_builder.expressions import (
    ActionExpression,
    ConditionsExpression,
    PlayGameExpression,
    RouteBuilderContext,
    RouteExpression,
    TLoadResult,
)
from botkit.routing.route_builder.has_route_collection import IRouteCollection
from botkit.routing.route_builder.route_collection import RouteCollection
from botkit.clients.client import IClient


class RouteBuilderBase(IRouteCollection):
    def __init__(
        self,
        routes: RouteCollection = None,
        current_client: IClient = None,
        context: RouteBuilderContext[TLoadResult] = None,
    ):
        self._route_collection: RouteCollection = (RouteCollection() if routes is None else routes)
        self._current_client: Optional[IClient] = (
            current_client or self._route_collection.current_client or None
        )
        self.context = context or RouteBuilderContext()

    @property
    def load_result(self) -> Optional[TLoadResult]:
        return self.context.load_result

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

        """
        TODO??: https://github.com/rubenlagus/TelegramBots/blob/master/telegrambots-abilities/src/main/java/org
        /telegram/abilitybots/api/objects/Privacy.java
        public enum Privacy {
              /**
               * Anybody who is not a bot admin or its creator will be considered as a public user.
               */
              PUBLIC,
              /**
               * Only group admins would get to initiate this command.
               */
              GROUP_ADMIN,
              /**
               * A global admin of the bot, regardless of the group the bot is in.
               */
              ADMIN,
              /**
               * The creator of the bot.
               */
              CREATOR
        }

        """

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
