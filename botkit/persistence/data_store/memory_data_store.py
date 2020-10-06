from collections import defaultdict
from typing import Optional

from haps import SINGLETON_SCOPE, egg, scope

from botkit.future_tgtypes.identities.chat_identity import ChatIdentity
from botkit.future_tgtypes.identities.message_identity import MessageIdentity
from botkit.persistence.data_store import DataStoreBase
from botkit.views.botkit_context import Context


@egg
@scope(SINGLETON_SCOPE)
class MemoryDataStore(DataStoreBase):
    def __init__(self):
        self._data = dict()

        def default_factory():
            return dict()

        self._data.setdefault("messages", defaultdict(default_factory))
        self._data.setdefault("users", defaultdict(default_factory))
        self._data.setdefault("chats", defaultdict(default_factory))
        self._data.setdefault("message_links", defaultdict(default_factory))

    async def retrieve_message_data(self, message_identity: Optional[MessageIdentity]):
        if not message_identity:
            return None
        return self._data["messages"][message_identity]

    async def retrieve_chat_data(self, chat_identity: Optional[ChatIdentity]):
        if not chat_identity:
            return None
        return self._data["chats"][chat_identity]

    async def retrieve_user_data(self, user_id: Optional[int]):
        if not user_id:
            return None
        return self._data["users"][user_id]

    async def synchronize_context_data(self, context: Context):
        # TODO: Add error handling when context is assigned to but that key does not exist (..though.. does it
        #  always..??)
        if user := context.user:
            self._data["users"][user.id] = context.user_state
        if chat := context.chat:
            chat_identity = ChatIdentity.from_chat_and_user(chat, user, context.client.own_user_id)
            self._data["chats"][chat_identity] = context.chat_state
        if message_identity := context.message_identity:
            self._data["messages"][message_identity] = context.message_state
