import asyncio
import re
from typing import *

from pydantic import root_validator
from pydantic.dataclasses import dataclass
from pyrogram import Client as PyrogramClient

from botkit.agnostic.resolvers import (
    resolve_chat_by_id,
    resolve_chat_by_title_regex,
    resolve_chat_by_username,
)
from botkit.clients.client import IClient
from botkit.future_tgtypes.descriptors.base import Descriptor
from botkit.future_tgtypes.identities.chat_identity import ChatIdentity
from botkit.future_tgtypes.primitives import Username
from botkit.utils.async_lazy_dict import AsyncLazyDict


@dataclass
class ChatDescriptor(Descriptor[ChatIdentity]):
    chat_id: Optional[int] = None
    username: Optional[Username] = None
    title_regex: Optional[str] = None

    async def resolve(self, client: IClient) -> ChatIdentity:
        context = AsyncLazyDict()
        identity = None

        try:
            if self.username and (
                identity := await resolve_chat_by_username(client, self.username, context)
            ):
                return identity

            if self.chat_id and (
                identity := await resolve_chat_by_id(client, self.chat_id, context)
            ):
                return identity

            if self.title_regex:
                if (
                    identity := await resolve_chat_by_title_regex(
                        client, re.compile(self.title_regex), context
                    )
                ) :
                    return identity
        except Exception as ex:
            raise ValueError(f"Could not resolve chat identity of {self}.", self) from ex

        raise ValueError(f"Could not resolve chat identity of {self}.", self)

    @classmethod
    async def resolve_many(
        cls, client: IClient, descriptors: List["ChatDescriptor"]
    ) -> List[ChatIdentity]:
        return await asyncio.gather(*[c.resolve(client) for c in descriptors])

    @root_validator(skip_on_failure=True)
    def at_least_one(cls, v: Dict) -> Dict:
        if not any((v.values())):
            raise ValueError(f"Descriptors must specify at least one of their fields.")
        return v
