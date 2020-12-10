from typing import Iterable, List

from haps import Container, Egg, SINGLETON_SCOPE, egg

from botkit.abstractions import IAsyncLoadUnload
from botkit.core.modules._module import Module
from botkit.utils.botkit_logging.setup import create_logger
from injector import Binder, Provider, inject, provider, Module, Injector, multiprovider, singleton

logger = create_logger()

# noinspection PyTypeHints
egg.factories: List[Egg]


def haps_disambiguate_module_eggs() -> List[Egg]:
    """
    Make all modules unambiguous to haps by settings its qualifier to the class name
    """
    eggs: List[Egg] = [m for m in egg.factories if m.base_ is Module]

    for e in eggs:
        e.qualifier = e.type_.__name__

    return eggs


def discover_modules(container: Container) -> List[Module]:
    haps_eggs: Iterable[Egg] = [m for m in container.config if m.base_ is Module]

    for e in haps_eggs:
        try:
            with container._lock:
                scope = container.scopes[SINGLETON_SCOPE]
                yield scope.get_object(e.egg)
        except:
            logger.exception("Could not retrieve object from scope")


def discover_async_loadable(container: Container) -> Iterable[IAsyncLoadUnload]:
    eggs: Iterable[Egg] = [m for m in container.config if IAsyncLoadUnload in m.base_.__bases__]

    for e in eggs:
        try:
            with container._lock:
                scope = container.scopes[SINGLETON_SCOPE]
                yield scope.get_object(e.egg)
        except:
            logger.exception("Could not retrieve object from scope")
