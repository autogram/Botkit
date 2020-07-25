from dataclasses import dataclass

from buslane.events import Event, EventHandler
from pyrogram import CallbackQuery, Client
from unittest.mock import Mock

from botkit.routing.route_builder.builder import RouteBuilder

client: Client = Mock(Client)
callback_query: CallbackQuery = Mock(CallbackQuery)


@dataclass
class TestEvent(Event):
    val: int


@dataclass
class TestEventHandler(EventHandler[TestEvent]):
    def handle(self, event: TestEvent) -> None:
        pass


def test_route_with_publish_expression_fires_event():
    ACTION = 123

    event = TestEvent(val=1)

    builder = RouteBuilder()
    builder.use(client)
    builder.on_action(ACTION).publish(event)

    route = builder._route_collection.routes_by_client[client][0]

    assert route.callback is not None
