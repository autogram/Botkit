from typing import Optional, Union
from uuid import UUID

from haps import egg

from ._base import ICallbackStore
from ._base import CallbackActionContext
from ._simple import (
    create_callback,
    lookup_callback,
)


@egg(qualifier="memory")
class MemoryDictCallbackManager(ICallbackStore):
    def create_callback(self, context: CallbackActionContext) -> str:
        return create_callback(context)

    def lookup_callback(self, id_: Union[str, UUID]) -> Optional[CallbackActionContext]:
        return lookup_callback(id_)

    def clear(self):
        pass

    def force_sync(self):
        pass

    def remove_outdated(self, days: int = 7):
        pass
