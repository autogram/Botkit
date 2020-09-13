from ._di import haps_disambiguate_module_eggs, resolve_modules
from ._module_activator import ModuleActivator
from ._module_loader import ModuleLoader
from ._module_status import ModuleStatus

haps_disambiguate_module_eggs()

__all__ = [
    "haps_disambiguate_module_eggs",
    "resolve_modules",
    "ModuleLoader",
    "ModuleActivator",
    "ModuleStatus",
]
