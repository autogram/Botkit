import inspect
import warnings
from typing import Any, Dict, List, Set, Type

import pyrogram
from more_itertools import flatten

from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.typed_callable import TypedCallable

PYROGRAM_UPDATE_TYPES: Dict[Type[pyrogram.Update], UpdateType] = {
    pyrogram.Message: UpdateType.message,
    pyrogram.CallbackQuery: UpdateType.callback_query,
    pyrogram.InlineQuery: UpdateType.inline_query,
    pyrogram.Poll: UpdateType.poll,
    # pyrogram.??? TODO: there is no one type to indicate user status
}

# noinspection PyUnresolvedReferences
PYROGRAM_HANDLER_TYPES: Dict[UpdateType, pyrogram.client.handlers.handler.Handler] = {
    UpdateType.message: pyrogram.MessageHandler,
    UpdateType.callback_query: pyrogram.CallbackQueryHandler,
    UpdateType.inline_query: pyrogram.InlineQueryHandler,
    UpdateType.poll: pyrogram.PollHandler,
    UpdateType.user_status: pyrogram.UserStatusHandler,
}


def determine_pyrogram_handler_update_types(handler: TypedCallable) -> Set[UpdateType]:
    used_arg_types = set(handler.type_hints.values())
    if not used_arg_types:
        raise ValueError(f"No type hints specified for handler {handler}.")

    used_update_types = list(flatten([_get_update_types(a) for a in used_arg_types]))

    # Early return if no subclasses of `Update` are found
    if not any(used_update_types):
        warnings.warn(
            f"The signature of {handler} does not appear to be a Pyrogram handler function (no update type found in "
            f"type annotations)."
        )

    # Find the concrete update type
    found_arg_types: Set[UpdateType] = set()
    for arg in used_update_types:
        for pyro_update_type, update_type in PYROGRAM_UPDATE_TYPES.items():
            if issubclass(arg, pyro_update_type):
                found_arg_types.add(update_type)
                break  # inner

    if not found_arg_types:
        raise ValueError(f"No matching update type found for handler {handler} with signature {handler.type_hints}.")

    return found_arg_types


def _get_update_types(t: Any) -> List[Type[pyrogram.Update]]:
    if _is_pyrogram_update_type(t):
        return [t]  # Direct subclass
    else:
        # Get classes out of Union type
        if (args := getattr(t, "__args__", None)) is not None:
            return [x for x in args if _is_pyrogram_update_type(x)]

    return []


def _is_pyrogram_update_type(t: Any) -> bool:
    return inspect.isclass(t) and issubclass(t, pyrogram.Update)
