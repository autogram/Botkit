import asyncio
from dataclasses import dataclass
from typing import Any, List
from unittest.mock import MagicMock, Mock

import pytest
from haps import Container, Egg
from pyrogram.types import CallbackQuery

from botkit.dispatching.callbackqueryactiondispatcher import CallbackQueryActionDispatcher
from botkit.dispatching.dispatcher import BotkitDispatcher
from botkit.libraries.annotations import IClient
from botkit.persistence import callback_store, data_store
from botkit.persistence.callback_store import CallbackStoreBase, MemoryDictCallbackManager
from botkit.persistence.data_store import DataStoreBase, MemoryDataStore
from botkit.routing.route import RouteDefinition
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.update_types.updatetype import UpdateType
from botkit.settings import botkit_settings
from botkit.views.botkit_context import Context

client: IClient = Mock(IClient)
callback_query: CallbackQuery = Mock(CallbackQuery)


@pytest.fixture(scope="function", autouse=True)
def configure_data_stores():
    Container.configure(
        [
            Egg(
                CallbackStoreBase,
                CallbackStoreBase,
                botkit_settings.callback_manager_qualifier,
                MemoryDictCallbackManager,
            ),
            Egg(DataStoreBase, DataStoreBase, None, MemoryDataStore,),
        ]
    )


def test_route_with_mutation_step_produces_valid_callback() -> None:

    ACTION = 123
    PAYLOAD = "after"

    @dataclass
    class MyModel:
        value: str = "before"

        def mutate_something_without_returning(self, context: Context):
            assert context.payload == PAYLOAD
            self.value = context.payload

    async def handle(
        client: IClient, callback_query: CallbackQuery, context: Context[MyModel, str]
    ) -> str:
        assert client is not None
        assert callback_query is not None
        assert context is not None
        assert context.payload == PAYLOAD
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

    state = MyModel()

    context: Context = Context(
        client=client,
        update=callback_query,
        view_state=state,
        action=ACTION,
        payload=PAYLOAD,
        update_type=UpdateType.callback_query,
    )

    asyncio.get_event_loop().run_until_complete(callback(client, callback_query, context))

    assert state.value == PAYLOAD


def test_full_with_dispatcher() -> None:
    ACTION = 123
    PAYLOAD = "after"

    @dataclass
    class MyModel:
        value: str = "before"

        def mutate_something_without_returning(self, context: Context):
            assert context.payload == PAYLOAD
            self.value = context.payload

    async def handle(
        client: IClient, callback_query: CallbackQuery, context: Context[MyModel, str]
    ) -> str:
        assert client is not None
        assert callback_query is not None
        assert context.view_state is not None
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

    state = MyModel()

    action_context: Context = Context(
        client=client,
        update=callback_query,
        view_state=state,
        action=ACTION,
        update_type=UpdateType.callback_query,
    )

    async def interject_handler(self, group: int, client: IClient, handler: Any):
        result = asyncio.get_event_loop().run_until_complete(
            callback(client, callback_query, action_context)
        )

        assert result == handle.__name__
        assert state.value == PAYLOAD

    dispatcher = BotkitDispatcher()
    callback_action_dispatcher = CallbackQueryActionDispatcher()
    dispatcher.callback_query_action_dispatchers[client] = callback_action_dispatcher
    dispatcher.add_handler = MagicMock()
    dispatcher.add_route_for_update_type(0, client, UpdateType.callback_query, route_handler)
    # TODO: add an actual test
