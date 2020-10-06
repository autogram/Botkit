import importlib

import sys
from typing import Literal
from typing import *

SupportedLibraryName = Literal["pyrogram", "telethon"]
SUPPORTED_LIBRARIES = ["pyrogram", "telethon"]

# noinspection PydanticTypeChecker
library_client_types: Dict[SupportedLibraryName, Type] = {}

try:
    from pyrogram import Client

    # noinspection PydanticTypeChecker
    library_client_types["pyrogram"] = Client
except:
    pass
try:
    from telethon import TelegramClient

    # noinspection PydanticTypeChecker
    library_client_types["telethon"] = TelegramClient
except:
    pass

__is_installed = lambda lib: lib in sys.modules
supported_library_installations = {lib: __is_installed(lib) for lib in SUPPORTED_LIBRARIES}


def is_installed(library: SupportedLibraryName) -> bool:
    ensure_supported(library)
    return supported_library_installations[library]


def ensure_installed(library: SupportedLibraryName) -> NoReturn:
    if not is_installed(library):
        raise ImportError(f"You cannot use {library} as it is not installed.")


def ensure_supported(library: SupportedLibraryName) -> NoReturn:
    if library not in SUPPORTED_LIBRARIES:
        raise KeyError(f"Sorry, the library '{library}' is not yet supported by Botkit.")


def client_is_instance(client: Any, library: SupportedLibraryName) -> bool:
    ensure_supported(library)
    if is_installed(library):
        client_cls = library_client_types[library]
        return isinstance(client, client_cls)
    return False
