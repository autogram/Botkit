from typing import (
    Iterable,
    Union,
    overload,
)
from uuid import uuid4

from .has_route_collection import IRouteCollection
from .state_route_builder import StateRouteBuilder


class StateMachineMixin(IRouteCollection):
    @overload
    def state_machine(self, states: Iterable[str]) -> Iterable[StateRouteBuilder]:
        ...

    @overload
    def state_machine(self, num_states: int) -> Iterable[StateRouteBuilder]:
        ...

    def state_machine(self, arg: Union[int, Iterable[str]]) -> Iterable[StateRouteBuilder]:
        machine_guid = uuid4()
        if isinstance(arg, int):
            for i in range(arg):
                yield StateRouteBuilder(machine_guid, i, self._route_collection)
        else:
            for i, name in enumerate(arg):
                yield StateRouteBuilder(machine_guid, i, self._route_collection, name=name)
