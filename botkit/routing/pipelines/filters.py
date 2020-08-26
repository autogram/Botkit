from typing import Awaitable, Callable

from pyrogram.types import Update

from botkit.libraries.annotations import IClient

UpdateFilterSignature = Callable[[IClient, Update], Awaitable[bool]]
