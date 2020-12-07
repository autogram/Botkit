from types import TracebackType
from typing import Any, AsyncContextManager, Awaitable, Dict, Generic, Optional, Type, TypeVar
from unittest.mock import Mock

from injector import Injector, InstanceProvider, Provider, Scope, ScopeDecorator


T = TypeVar("T")
TEventContext = TypeVar("TEventContext")


class EventScope(Scope, Generic[TEventContext]):
    """
    TODO: Make it a context manager and free up instantiated resources after the event pipeline is done.
    """

    REGISTRY_KEY = "UpdateScopeRegistry"

    _instances: Dict[Type, Provider]

    def __init__(self, injector: Injector, context: TEventContext):
        super().__init__(injector)
        self._event_context = context

    def configure(self) -> None:
        self._instances = {}

    def get(self, key: Type[T], provider: Provider[T]) -> Provider[T]:
        try:
            return self._instances[key]
        except KeyError:
            provider = InstanceProvider(provider.get(self.injector))
            self._instances[key] = provider
            return provider


update_scope = ScopeDecorator(EventScope)
