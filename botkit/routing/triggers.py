from dataclasses import dataclass

from pyrogram.client.filters.filter import Filter
from typing import Optional, Callable, Union, Awaitable

ActionIdTypes = Union[int, str]


@dataclass(frozen=True)
class RouteTriggers:
    filters: Optional[Filter] = None
    action: Optional[ActionIdTypes] = None
    condition: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None
