import asyncio
from dataclasses import dataclass
from typing import Any, List
from unittest.mock import MagicMock, Mock

from pyrogram import filters
from pyrogram.types import CallbackQuery

from botkit.dispatching.callbackqueries.callbackactiondispatcher import CallbackActionDispatcher
from botkit.dispatching.dispatcher import BotkitDispatcher
from botkit.libraries.annotations import IClient
from botkit.routing.route import RouteDefinition
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.typed_callable import TypedCallable
from botkit.views.botkit_context import Context

client: IClient = Mock(IClient)
callback_query: CallbackQuery = Mock(CallbackQuery)


def test_route_with_mutation_step_produces_valid_callback() -> None:
    ACTION = 123
    PAYLOAD = "after"

    @dataclass
    class MyModel:
        value: str = "before"

        def mutate_something_without_returning(self, context: Context):
            assert context.payload == PAYLOAD
            self.value = context.payload

    async def handle(client: IClient, callback_query: CallbackQuery, state: MyModel) -> str:
        assert client is not None
        assert callback_query is not None
        assert state is not None
        return handle.__name__

    builder = RouteBuilder()

    builder.use(client)
    builder.on_action(ACTION).mutate(MyModel.mutate_something_without_returning).then_call(handle)

    routes: List[RouteDefinition] = builder._route_collection.routes_by_client[client]
    route = routes[0]
    del builder

    assert route.triggers.filters is None
    assert route.triggers.action == ACTION
    assert UpdateType.callback_query in route.handler_by_update_type
    callback = route.handler_by_update_type[UpdateType.callback_query].callback
    assert TypedCallable(callback).type_hints == {
        "client": IClient,
        "callback_query": CallbackQuery,
        "context": Context,
        "return": str,
    }

    state = MyModel()

    action_context: Context = Context(
        client=client, update=callback_query, state=state, action=ACTION, payload=PAYLOAD
    )

    result = asyncio.get_event_loop().run_until_complete(
        callback(client, callback_query, state, action_context)
    )

    assert result == handle.__name__
    assert state.value == PAYLOAD


def test_route_with_gather_step_produces_valid_callback() -> None:
    ACTION = "my-action"
    EXPECTATION = "after"

    @dataclass
    class MyModel:
        value: str = "before"

    async def handle(client: IClient, callback_query: CallbackQuery, state: MyModel) -> MyModel:
        assert client is not None
        assert callback_query is not None
        assert state is not None
        return state

    flt = filters.text

    builder = RouteBuilder()
    builder.use(client)
    builder.on(flt).gather(lambda: MyModel(value=EXPECTATION)).then_call(handle)

    routes: List[RouteDefinition] = builder._route_collection.routes_by_client[client]
    route = routes[0]

    assert route.triggers.filters is flt
    assert UpdateType.callback_query in route.handler_by_update_type
    callback = route.handler_by_update_type[UpdateType.callback_query].callback
    assert TypedCallable(callback).type_hints == {
        "client": IClient,
        "callback_query": CallbackQuery,
        "state": MyModel,
        "return": MyModel,
    }

    action_context: Context = Context(
        client=client, update=callback_query, state=MyModel(), action=ACTION
    )

    state = asyncio.get_event_loop().run_until_complete(
        callback(client, callback_query, None, action_context)
    )

    assert isinstance(state, MyModel)
    assert state.value == EXPECTATION


def test_full_with_dispatcher() -> None:
    ACTION = 123
    PAYLOAD = "after"

    @dataclass
    class MyModel:
        value: str = "before"

        def mutate_something_without_returning(self, context: Context):
            assert context.payload == PAYLOAD
            self.value = context.payload

    async def handle(client: IClient, callback_query: CallbackQuery, state: MyModel) -> str:
        assert client is not None
        assert callback_query is not None
        assert state is not None
        return handle.__name__

    builder = RouteBuilder()

    builder.use(client)
    builder.on_action(ACTION).mutate(MyModel.mutate_something_without_returning).then_call(handle)

    routes: List[RouteDefinition] = builder._route_collection.routes_by_client[client]
    route = routes[0]
    del builder

    assert route.triggers.filters is None
    assert route.triggers.action == ACTION
    assert UpdateType.callback_query in route.handler_by_update_type
    route_handler = route.handler_by_update_type[UpdateType.callback_query]
    callback = route_handler.callback
    assert TypedCallable(callback).type_hints == {
        "client": IClient,
        "callback_query": CallbackQuery,
        "state": MyModel,
        "return": str,
    }

    state = MyModel()

    action_context: Context = Context(
        client=client, update=callback_query, state=state, action=ACTION
    )

    async def interject_handler(self, group: int, client: IClient, handler: Any):
        result = asyncio.get_event_loop().run_until_complete(
            callback(client, callback_query, state, action_context)
        )

        assert result == handle.__name__
        assert state.value == PAYLOAD

    dispatcher = BotkitDispatcher()
    callback_action_dispatcher = CallbackActionDispatcher()
    dispatcher.callback_action_dispatchers[client] = callback_action_dispatcher
    dispatcher.add_handler = MagicMock()
    dispatcher.add_route_for_update_type(0, client, UpdateType.callback_query, route_handler)
    dispatcher.add_handler.assert_called_once_with(
        0, client, callback_action_dispatcher.pyrogram_handler
    )
