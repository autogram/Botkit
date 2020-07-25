from typing import Callable

from pyrogram import Update

UpdateFilterSignature = Callable[[Update], bool]
