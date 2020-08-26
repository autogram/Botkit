from dataclasses import dataclass

from typing import Optional, Callable, Union, Awaitable

from pyrogram.filters import Filter

from botkit.routing.pipelines.filters import UpdateFilterSignature

ActionIdTypes = Union[int, str]


@dataclass(frozen=True)
class RouteTriggers:
    filters: Optional[Filter] = None
    action: Optional[ActionIdTypes] = None
    condition: Optional[Callable[[], Union[bool, Awaitable[bool]]]] = None
