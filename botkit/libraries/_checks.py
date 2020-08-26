import sys
from typing import Literal

SupportedLibrary = Literal["pyrogram"]


def is_installed(library: SupportedLibrary) -> bool:
    return library in sys.modules
