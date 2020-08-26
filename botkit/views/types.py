from typing import Tuple, TypeVar, Union

from pyrogram.types import InlineKeyboardButton

KeyboardTypes = Union[InlineKeyboardButton, Tuple]
TState = TypeVar("TState")
