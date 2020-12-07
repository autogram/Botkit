from abc import ABC, abstractmethod
from typing import Optional

from haps import base

from botkit.botkit_context import Context
from tgtypes.identities.chat_identity import ChatIdentity
from tgtypes.identities.message_identity import MessageIdentity


@base
class DataStoreBase(ABC):
    @abstractmethod
    async def retrieve_message_data(self, message_identity: Optional[MessageIdentity]):
        ...

    @abstractmethod
    async def retrieve_chat_data(self, chat_identity: Optional[ChatIdentity]):
        ...

    @abstractmethod
    async def retrieve_user_data(self, user_id: Optional[int]):
        ...

    @abstractmethod
    async def synchronize_context_data(self, context: Context):
        pass  # TODO
