from typing import Awaitable, Callable

from pyrogram.types import Update

from botkit.clients.client import IClient

UpdateFilterSignature = Callable[[IClient, Update], Awaitable[bool]]
