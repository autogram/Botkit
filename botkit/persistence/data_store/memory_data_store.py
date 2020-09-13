from collections import defaultdict

from haps import SINGLETON_SCOPE, egg, scope

from botkit.future_tgtypes.chat_descriptor import ChatDescriptor
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

    async def fill_context_data(self, context: Context) -> None:
        if user := context.user:
            context.user_state = self._data["users"][user.id]
        if chat := context.chat:
            chat_descriptor = ChatDescriptor.from_chat_and_user(
                chat, user, context.client.me_user_id
            )
            context.chat_state = self._data["chats"][chat_descriptor]
        if message_descriptor := context.message_descriptor:
            context.message_state = self._data["messages"][message_descriptor]

    async def synchronize_context_data(self, context: Context):
        # TODO: Add error handling when context is assigned to but that key does not exist (..though.. does it
        #  always..??)
        if user := context.user:
            self._data["users"][user.id] = context.user_state
        if chat := context.chat:
            chat_descriptor = ChatDescriptor.from_chat_and_user(
                chat, user, context.client.me_user_id
            )
            self._data["chats"][chat_descriptor] = context.chat_state
        if message_descriptor := context.message_descriptor:
            self._data["messages"][message_descriptor] = context.message_state
