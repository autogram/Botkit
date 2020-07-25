from typing import Iterable, List

from haps import Container, Egg, SINGLETON_SCOPE, egg
from haps.config import Configuration

from ._module import Module

# noinspection PyTypeHints
egg.factories: List[Egg]


def haps_disambiguate_module_eggs() -> List[Egg]:
    """
    # Make all modules unambiguous to haps by settings its qualifier to the class name
    """
    eggs: List[Egg] = [m for m in egg.factories if m.base_ is Module]

    for e in eggs:
        e.qualifier = e.type_.__name__

    return eggs


@Configuration.resolver("modules")
def resolve_modules() -> List[Module]:
    return list(discover_modules(Container()))


def discover_modules(container: Container) -> Iterable[Module]:
    eggs: Iterable[Egg] = [m for m in container.config if m.base_ is Module]

    for e in eggs:
        scope = container.scopes[SINGLETON_SCOPE]
        with container._lock:
            yield scope.get_object(e.egg)
