import traceback
from abc import ABCMeta, abstractmethod
from typing import Dict, TypeVar, Any, List

from haps import *
from telethon.tl.custom import Message, Dialog

from commons.core.clients.userclient import IUserClient
from commons.core.descriptors.base import EntityDescriptor
from commons.core.util import string_similarity
from telethon.tl import TLObject
from telethon.utils import get_display_name as telethon_get_display_name

T = TypeVar("P")


class EntityNotFoundError(Exception):
    pass


def get_display_name(entity: Any):
    if isinstance(entity, Dialog):
        return entity.name
    if hasattr(entity, "title"):
        return entity.title
    return telethon_get_display_name(entity)


@base
class ILookupService(ABC):
    @abstractmethod
    async def resolve_peer(self, descriptor: EntityDescriptor, raise_=True):
        pass

    @abstractmethod
    async def resolve_full_peer(self, descriptor: EntityDescriptor):
        pass

    @abstractmethod
    async def get_message_by_id(self, chat: Any, message_id: int) -> Message:
        pass

    @abstractmethod
    async def get_previous_messages(self, event: Event, n: int = 1) -> List[Message]:
        pass

    @abstractmethod
    async def get_last_message_in_chat(self, input_chat: Any) -> Message:
        pass


@egg
class LookupService(ILookupService):
    client: IUserClient = Inject()

    _entity_cache: Dict[EntityDescriptor, TLObject]

    async def resolve_peer(self, descriptor: EntityDescriptor, raise_=True):
        if descriptor.chat_id:
            return await self.client.get_input_entity(descriptor.chat_id)
        if descriptor.username:
            return await self.client.get_input_entity(descriptor.username)
        if descriptor.title:
            return await self._resolve_chat_by_title(descriptor.title, raise_=raise_)
        raise NotImplementedError("Descriptor has an unknown property.")

    async def resolve_full_peer(self, descriptor: EntityDescriptor):
        return self.client.session.get_input_entity(descriptor)

    async def _resolve_chat_by_title(
        self, title: str, confidence=0.9, aggressive=False, raise_=True
    ) -> TLObject:
        results = await self.client.get_dialogs(limit=200)

        def matches_query(found_name):
            sim = string_similarity(title, found_name)
            if sim > confidence:
                return True
            return False

        for d in results:
            if matches_query(get_display_name(d)):
                return d

        if raise_:
            raise EntityNotFoundError
        else:
            return None

    async def _resolve_user_by_title(
        self, title: str, confidence=0.9, aggressive=False, raise_=True
    ) -> TLObject:
        results = await self.client.get_dialogs(limit=40)

        def matches_query(found_name):
            sim = string_similarity(title, found_name)
            if sim > confidence:
                return True
            return False

        # Search failed.
        for d in results:
            try:
                participants = self.client.iter_participants(
                    d.input_entity, 200, search="", aggressive=aggressive
                )
                async for p in participants:
                    if matches_query(get_display_name(p)):
                        return p.entity
            except:
                traceback.print_exc()

        if raise_:
            raise EntityNotFoundError
        else:
            return None

    async def get_message_by_id(self, chat: Any, message_id: int) -> Message:
        raise NotImplemented  # TODO

    async def get_previous_messages(self, event: Event, n: int = 1) -> List[Message]:
        limit = n + 1
        return (await self.client.get_messages(entity=event.input_chat, limit=limit))[:-1]

    async def get_last_message_in_chat(self, input_chat: Any) -> Message:
        return (await self.client.get_messages(input_chat, limit=1))[0]
