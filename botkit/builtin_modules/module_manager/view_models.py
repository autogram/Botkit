from boltons.iterutils import flatten
from pydantic import BaseModel
from typing import List, Iterable

from botkit.core.moduleloader import ModuleLoader, ModuleStatus
from botkit.core.modules._module import Module
from botkit.builtin_modules.module_manager.pagination_model import PaginationModel
from botkit.inlinequeries.contexts import PrefixBasedInlineModeContext


class ModuleInfo(BaseModel):
    name: str
    route_descriptions: List[str]
    module_state: ModuleStatus

    @classmethod
    def from_module(cls, module: Module, loader: ModuleLoader) -> "ModuleInfo":
        return ModuleInfo(
            name=module.get_name(),
            route_descriptions=[
                m.description for m in flatten(module.route_collection.routes_by_client.values())
            ],
            module_state=loader.get_module_status(module),
        )

    @property
    def is_active(self):
        return self.module_state == ModuleStatus.active


class ModuleInfosCollectionModel(PaginationModel[ModuleInfo]):
    def __init__(self, all_items: Iterable[ModuleInfo]):
        super().__init__(all_items, items_per_page=1)


class ModuleInlineContext(PrefixBasedInlineModeContext):
    pass
