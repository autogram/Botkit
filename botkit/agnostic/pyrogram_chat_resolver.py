import asyncio
from datetime import timedelta
from typing import (
    Optional,
    Pattern,
    cast,
)

from pyrogram.errors import BotMethodInvalid

from botkit.tghelpers.names import display_name
from botkit.utils.botkit_logging.setup import create_logger
from tgtypes.interfaces.resolvercache import IResolverCache
from tgtypes.persistence.json_file_resolver_cache import JsonFileResolverCache
from tgtypes.utils.debounce import DebouncedTask
from tgtypes.primitives import Username
from tgtypes.identities.chat_identity import ChatIdentity, ChatType
from tgtypes.interfaces.chatresolver import IChatResolver

try:
    # TODO: Turn this into a contextmanager, `with lib_check('Pyrogram'): import ...`
    from pyrogram import Client as PyrogramClient
    from pyrogram.types import Chat, Message, User
except ImportError as e:
    raise ImportError(
        "The Pyrogram library does not seem to be installed, so using Botkit in Pyrogram flavor is not possible. "
    ) from e

log = create_logger("chat_resolver")


class PyrogramChatResolver(IChatResolver):
    def __init__(self, client: PyrogramClient, cache: Optional[IResolverCache] = None):
        self.client = client
        self.cache: IResolverCache = cache or JsonFileResolverCache()
        self._iter_dialogs_lock = asyncio.Lock()
        self._save_func = DebouncedTask(
            lambda: self.cache.dump_data(), delta=timedelta(seconds=20), num_runs=3
        )

    async def resolve_chat_by_username(self, username: Username) -> ChatIdentity:
        await self.cache.ensure_initialized()
        chat = await self.cache.setdefault_lazy("chat", self.client.get_chat(username))
        return ChatIdentity(type=cast(ChatType, chat.type), peers=chat.id)

    async def resolve_chat_by_chat_id(self, chat_id: int) -> ChatIdentity:
        await self.cache.ensure_initialized()
        chat = await self.cache.setdefault_lazy("chat", self.client.get_chat(chat_id))
        return ChatIdentity(type=cast(ChatType, chat.type), peers=chat.id)

    async def resolve_chat_by_title_regex(self, title_regex: Pattern) -> ChatIdentity:
        await self.cache.ensure_initialized()
        LIMIT = 500

        self.cache.setdefault("identity_titles", [])

        try:
            # In order to make use of caching, disallow running multiple iter_dialogs methods concurrently
            async with self._iter_dialogs_lock:
                # Check cached items first
                for ident, t in self.cache["identity_titles"]:
                    if title_regex.match(t):
                        return ident

                async for d in self.client.iter_dialogs(limit=LIMIT):
                    chat: Chat = getattr(d, "chat", None)

                    if not chat:
                        continue

                    title: str = display_name(chat)
                    identity = ChatIdentity(type=cast(ChatType, chat.type), peers=chat.id)

                    self.cache["identity_titles"].append((identity, title))

                    # noinspection PyUnboundLocalVariable
                    if title_regex.match(title):
                        return identity

            raise ValueError(
                f"No chat found matching pattern {title_regex} in the uppermost {LIMIT} dialogs."
            )
        except BotMethodInvalid as ex:
            raise ValueError(
                "Method invalid: Bots cannot read chat lists and thus not match via `title_regex`. "
                "You should resolve with a user client instead."
            ) from ex
