from typing import Optional, Union
from uuid import UUID

from ._base import CallbackActionContext, ICallbackManager
from ._simple import (
    create_callback,
    lookup_callback,
)


class LocalDictCallbackManager(ICallbackManager):
    def create_callback(self, context: CallbackActionContext) -> str:
        return create_callback(context)

    def lookup_callback(self, id_: Union[str, UUID]) -> Optional[CallbackActionContext]:
        return lookup_callback(id_)

    def clear(self):
        pass

    def force_sync(self):
        pass
