import sys
from typing import Literal

SupportedLibraries = Literal["pyrogram", "telethon"]


def is_installed(library: SupportedLibraries) -> bool:
    return library in sys.modules


def ensure_installed(library: SupportedLibraries):
    if not is_installed(library):
        raise ImportError(f"You cannot use {library} as it is not installed.")
