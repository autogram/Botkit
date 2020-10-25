from contextlib import contextmanager
from typing import *
from re import Pattern as PatternType

from botkit.agnostic.library_checks import client_is_instance
from botkit.clients.client import IClient
from botkit.future_tgtypes.identities.chat_identity import ChatIdentity
from botkit.future_tgtypes.primitives import Username
from botkit.utils.async_lazy_dict import AsyncLazyDict
from botkit.utils.nameof import nameof

try:
    from pyrogram import Client as PyrogramClient
except:
    pass
try:
    from telethon import TelegramClient as TelethonClient
except:
    pass


async def resolve_chat_by_username(
    client: IClient, username: Username, context: AsyncLazyDict
) -> ChatIdentity:
    if client_is_instance(client, "pyrogram"):
        client = cast(PyrogramClient, client)

        res = await context.setdefault_lazy("chat", client.get_chat(username))
        # noinspection PydanticTypeChecker
        return ChatIdentity(type=res.type, peers=res.id)
    else:
        raise NotImplementedError(f"No implementation for {nameof(resolve_chat_by_username)} yet.")


async def resolve_chat_by_id(
    client: IClient, chat_id: int, context: AsyncLazyDict
) -> ChatIdentity:
    if client_is_instance(client, "pyrogram"):
        client = cast(PyrogramClient, client)

        res = await context.setdefault_lazy("chat", client.get_chat(chat_id))
        # noinspection PydanticTypeChecker
        return ChatIdentity(type=res.type, peers=res.id)
    else:
        raise NotImplementedError(f"No implementation for {nameof(resolve_chat_by_id)} yet.")


async def resolve_chat_by_title_regex(
    client: IClient, title_regex: PatternType, _: AsyncLazyDict
) -> ChatIdentity:
    LIMIT = 1000

    if client_is_instance(client, "pyrogram"):
        client = cast(PyrogramClient, client)

        async for d in client.iter_dialogs(limit=LIMIT):
            if (
                (chat := getattr(d, "chat", None))
                and (title := getattr(chat, "title", None))
                and title_regex.match(title)
            ):
                return ChatIdentity(type=chat.type, peers=chat.id)

        raise ValueError(
            f"No chat found matching pattern {title_regex} in the uppermost {LIMIT} dialogs."
        )
    else:
        raise NotImplementedError(f"No implementation for {nameof(resolve_chat_by_username)} yet.")
