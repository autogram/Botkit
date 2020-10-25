from typing import Set

from botkit.agnostic._pyrogram_update_type_inference import determine_pyrogram_handler_update_types
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.typed_callable import TypedCallable


def infer_update_types(handler: TypedCallable) -> Set[UpdateType]:
    return determine_pyrogram_handler_update_types(handler)
