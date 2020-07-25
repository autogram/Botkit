import asyncio
from dataclasses import dataclass
from typing import List
from unittest.mock import MagicMock, Mock

from pyrogram import CallbackQuery, Client, Filters
from pyrogram.client.handlers.handler import Handler

from botkit.dispatching.callbackqueries.callbackactioncontext import CallbackActionContext
from botkit.dispatching.callbackqueries.callbackactiondispatcher import CallbackActionDispatcher
from botkit.dispatching.dispatcher import BotkitDispatcher
from botkit.routing.route import RouteDefinition
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.typed_callable import TypedCallable

client: Client = Mock(Client)
callback_query: CallbackQuery = Mock(CallbackQuery)


def test_route_with_mutation_step_produces_valid_callback() -> None:
    ACTION = 123
    PAYLOAD = "after"

    @dataclass
    class TestModel:
        value: str = "before"

        def mutate_something_without_returning(self, context: CallbackActionContext):
            assert context.payload == PAYLOAD
            self.value = context.payload

    async def handle(client: Client, callback_query: CallbackQuery, state: TestModel) -> str:
        assert client is not None
        assert callback_query is not None
        assert state is not None
        return handle.__name__

    builder = RouteBuilder()

    builder.use(client)
    builder.on_action(ACTION).mutate(TestModel.mutate_something_without_returning).then_call(handle)

    routes: List[RouteDefinition] = builder._route_collection.routes_by_client[client]
    route = routes[0]
    del builder

    assert route.triggers.filters is None
    assert route.triggers.action == ACTION
    assert UpdateType.callback_query in route.handler_by_update_type
    callback = route.handler_by_update_type[UpdateType.callback_query].callback
    assert TypedCallable(callback).type_hints == {
        "client": Client,
        "callback_query": CallbackQuery,
        "state": TestModel,
        "return": str,
    }

    state = TestModel()

    action_context: CallbackActionContext = CallbackActionContext(action=ACTION, payload=PAYLOAD)

    result = asyncio.get_event_loop().run_until_complete(callback(client, callback_query, state, action_context))

    assert result == handle.__name__
    assert state.value == PAYLOAD


def test_route_with_gather_step_produces_valid_callback() -> None:
    ACTION = "my-action"
    EXPECTATION = "after"

    @dataclass
    class TestModel:
        value: str = "before"

    async def handle(client: Client, callback_query: CallbackQuery, state: TestModel) -> TestModel:
        assert client is not None
        assert callback_query is not None
        assert state is not None
        return state

    filters = Filters.text

    builder = RouteBuilder()
    builder.use(client)
    builder.on(filters).gather(lambda: TestModel(value=EXPECTATION)).then_call(handle)

    routes: List[RouteDefinition] = builder._route_collection.routes_by_client[client]
    route = routes[0]

    assert route.triggers.filters is filters
    assert UpdateType.callback_query in route.handler_by_update_type
    callback = route.handler_by_update_type[UpdateType.callback_query].callback
    assert TypedCallable(callback).type_hints == {
        "client": Client,
        "callback_query": CallbackQuery,
        "state": TestModel,
        "return": TestModel,
    }

    action_context: CallbackActionContext = CallbackActionContext(action=ACTION)

    state = asyncio.get_event_loop().run_until_complete(callback(client, callback_query, None, action_context))

    assert isinstance(state, TestModel)
    assert state.value == EXPECTATION


def test_full_with_dispatcher() -> None:
    ACTION = 123
    PAYLOAD = "after"

    @dataclass
    class TestModel:
        value: str = "before"

        def mutate_something_without_returning(self, context: CallbackActionContext):
            assert context.payload == PAYLOAD
            self.value = context.payload

    async def handle(client: Client, callback_query: CallbackQuery, state: TestModel) -> str:
        assert client is not None
        assert callback_query is not None
        assert state is not None
        return handle.__name__

    builder = RouteBuilder()

    builder.use(client)
    builder.on_action(ACTION).mutate(TestModel.mutate_something_without_returning).then_call(handle)

    routes: List[RouteDefinition] = builder._route_collection.routes_by_client[client]
    route = routes[0]
    del builder

    assert route.triggers.filters is None
    assert route.triggers.action == ACTION
    assert UpdateType.callback_query in route.handler_by_update_type
    route_handler = route.handler_by_update_type[UpdateType.callback_query]
    callback = route_handler.callback
    assert TypedCallable(callback).type_hints == {
        "client": Client,
        "callback_query": CallbackQuery,
        "state": TestModel,
        "return": str,
    }

    state = TestModel()

    action_context: CallbackActionContext = CallbackActionContext(action=ACTION, payload=PAYLOAD)

    async def interject_handler(self, group: int, client: Client, handler: Handler):
        result = asyncio.get_event_loop().run_until_complete(callback(client, callback_query, state, action_context))

        assert result == handle.__name__
        assert state.value == PAYLOAD

    dispatcher = BotkitDispatcher()
    callback_action_dispatcher = CallbackActionDispatcher()
    dispatcher.callback_action_dispatchers[client] = callback_action_dispatcher
    dispatcher.add_handler = MagicMock()
    dispatcher.add_route_for_update_type(0, client, UpdateType.callback_query, route_handler)
    dispatcher.add_handler.assert_called_once_with(0, client, callback_action_dispatcher.pyrogram_handler)
