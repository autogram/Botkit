from typing import cast
from unittest.mock import Mock

import pytest
from pyrogram import filters
from pyrogram.types import Message

from botkit.core.modules import Module
from botkit.agnostic.annotations import IClient
from botkit.routing.route_builder.builder import RouteBuilder
from botkit.routing.route_builder.state_route_builder import StateRouteBuilder

client: IClient = Mock(IClient)


def test_stuff():
    routes = RouteBuilder()
    routes.use(client)

    dontuse = 7
    a, b, c = routes.state_machine()

    a.on()

    d, e = routes.state_machine()

    assert a.name == "a"
    assert b.name == "b"
    assert c.name == "c"


def test_state_machine_initialization_via_ast():
    routes = RouteBuilder()
    routes.use(client)

    entry_point, a, b, done = routes.state_machine(4)

    assert isinstance(entry_point, StateRouteBuilder)
    assert isinstance(a, StateRouteBuilder)
    assert isinstance(b, StateRouteBuilder)
    assert isinstance(done, StateRouteBuilder)


def test_state_machine_initialization_via_num_arguments():
    routes = RouteBuilder()
    routes.use(client)

    entry_point, a, b, done = routes.state_machine(4)

    assert isinstance(entry_point, StateRouteBuilder)
    assert isinstance(a, StateRouteBuilder)
    assert isinstance(b, StateRouteBuilder)
    assert isinstance(done, StateRouteBuilder)


def test_state_machine_initialization_via_named_states():
    routes = RouteBuilder()
    routes.use(client)

    entry_point, a, b, done = routes.state_machine(["entry_point", "a", "b", "done"])

    assert entry_point.name == "entry_point"
    assert a.name == "a"
    assert b.name == "b"
    assert done.name == "done"


def test_state_machine_invalid_number_of_states_raises():
    routes = RouteBuilder()
    routes.use(client)

    with pytest.raises(ValueError):
        entry_point, b = routes.state_machine(3)


class StateMachineTestModule(Module):
    def register(self, routes: RouteBuilder):
        routes.use(client)

        entry_points, ended = routes.state_machine(2)

        entry_points = cast(StateRouteBuilder, entry_points)
        ended = cast(StateRouteBuilder, ended)

        def entry_point(client: IClient, message: Message):
            pass

        def end(client: IClient, message: Message):
            pass

        entry_points.on(filters.text).call(entry_point).and_transition_to(ended)
        ended.on(filters.text).call(end).and_exit_state()


def test_state_machine_routing():
    pass
    # module = StateMachineTestModule()
    # dispatcher = BotkitDispatcher()
    #
    # collection = register_module_with_route_builder(module, RouteBuilder)
    #
    # relevant_routes: List[Route] = collection.routes_by_client[client]
    #
    # message = Mock(view_sender_interface)
    # message.configure_mock(text="henlo")
    #
    # assert len(relevant_routes) == 2
    #
    # entry_point = relevant_routes[0].pyrogram_handlers
    # end = relevant_routes[1].pyrogram_handlers
    #
    # assert entry_point.check(message)
    # res = entry_point.callback(client, message)
    # assert res is None
