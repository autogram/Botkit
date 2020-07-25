from boltons.iterutils import flatten
from pydantic import BaseModel
from typing import List, Iterable

from botkit.core.moduleloader import ModuleLoader
from botkit.core.modules._module import Module
from botkit.botkit_modules.module_manager.pagination_model import PaginationModel
from botkit.inlinequeries.contexts import PrefixBasedInlineModeContext


class ModuleInfo(BaseModel):
    name: str
    route_descriptions: List[str]
    is_enabled: bool

    @classmethod
    def from_module(cls, module: Module, loader: ModuleLoader) -> "ModuleInfo":
        return ModuleInfo(
            name=module.get_name(),
            route_descriptions=[m.description for m in flatten(module.route_collection.routes_by_client.values())],
            is_enabled=loader.is_active(module),
        )


class ModuleInfosCollectionModel(PaginationModel[ModuleInfo]):
    def __init__(self, all_items: Iterable[ModuleInfo]):
        super().__init__(all_items, items_per_page=1)


class ModuleInlineContext(PrefixBasedInlineModeContext):
    pass
