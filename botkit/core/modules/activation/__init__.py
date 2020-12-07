from typing import List

from haps.container import Container
from ._di import discover_modules, haps_disambiguate_module_eggs
from ._module_activator import ModuleActivator
from ._module_loader import ModuleLoader
from ._module_status import ModuleStatus
from injector import Binder

from .. import Module


def configure_module_activation(binder: Binder):
    binder.multibind(List[Module], lambda: list(discover_modules(Container())))


haps_disambiguate_module_eggs()

__all__ = [
    "configure_module_activation",
    "haps_disambiguate_module_eggs",
    "ModuleLoader",
    "ModuleActivator",
    "ModuleStatus",
]
