from typing import (
    Optional,
    Union,
    Dict,
)
from uuid import UUID

from ._base import generate_id
from ._base import CallbackActionContext

__callbacks: Dict[str, Dict] = dict()


def create_callback(context: CallbackActionContext) -> str:
    id_ = generate_id()

    __callbacks[id_] = context.dict()

    return id_


def lookup_callback(id_: Union[str, UUID]) -> Optional[CallbackActionContext]:
    context: Optional[Dict] = __callbacks.get(str(id_))
    if context is None:
        return None
    return CallbackActionContext(**context)
