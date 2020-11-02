from typing import Pattern, cast

from botkit.utils.botkit_logging.setup import create_logger
from tgtypes.identities.chat_identity import ChatIdentity, ChatType
from tgtypes.interfaces.chatresolver import IChatResolver
from tgtypes.primitives import Username
from tgtypes.utils.async_lazy_dict import AsyncLazyDict

try:
    # TODO: Turn this into a contextmanager, `with lib_check('Pyrogram'): import ...`
    from pyrogram import Client as PyrogramClient
    from pyrogram.types import Message, User
except ImportError as e:
    raise ImportError(
        "The Pyrogram library does not seem to be installed, so using Botkit in Pyrogram flavor is not possible. "
    ) from e

log = create_logger("chat_resolver")


class PyrogramChatResolver(IChatResolver):
    def __init__(self, client: PyrogramClient):
        self.client = client
        self.context = AsyncLazyDict()

    async def resolve_chat_by_username(self, username: Username) -> ChatIdentity:
        chat = await self.context.setdefault_lazy("chat", self.client.get_chat(username))
        return ChatIdentity(type=cast(ChatType, chat.type), peers=chat.id)

    async def resolve_chat_by_chat_id(self, chat_id: int) -> ChatIdentity:
        chat = await self.context.setdefault_lazy("chat", self.client.get_chat(chat_id))
        return ChatIdentity(type=cast(ChatType, chat.type), peers=chat.id)

    async def resolve_chat_by_title_regex(self, title_regex: Pattern) -> ChatIdentity:
        LIMIT = 1000

        async for d in self.client.iter_dialogs(limit=LIMIT):
            # noinspection PyUnboundLocalVariable
            if (
                (chat := getattr(d, "chat", None))
                and (title := getattr(chat, "title", None))
                and title_regex.match(title)
            ):
                return ChatIdentity(type=cast(ChatType, chat.type), peers=chat.id)

        raise ValueError(
            f"No chat found matching pattern {title_regex} in the uppermost {LIMIT} dialogs."
        )
