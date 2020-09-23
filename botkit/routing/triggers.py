from dataclasses import dataclass, field

from typing import Optional, Callable, Set, Union, Awaitable

from boltons.iterutils import is_collection
from pyrogram.filters import Filter

from botkit.routing.update_types.updatetype import UpdateType

ActionIdType = Union[int, str]


@dataclass
class RouteTriggers:
    filters: Optional[Filter] = None
    action: Optional[ActionIdType] = None
    condition: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None
