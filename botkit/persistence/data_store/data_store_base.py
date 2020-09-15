from abc import ABC, abstractmethod
from typing import Optional

from haps import base

from botkit.future_tgtypes.chat_descriptor import ChatDescriptor
from botkit.future_tgtypes.message_descriptor import MessageDescriptor
from botkit.views.botkit_context import Context


@base
class DataStoreBase(ABC):
    @abstractmethod
    async def retrieve_message_data(self, message_descriptor: Optional[MessageDescriptor]):
        ...

    @abstractmethod
    async def retrieve_chat_data(self, chat_descriptor: Optional[ChatDescriptor]):
        ...

    @abstractmethod
    async def retrieve_user_data(self, user_id: Optional[int]):
        ...

    @abstractmethod
    async def synchronize_context_data(self, context: Context):
        pass  # TODO
