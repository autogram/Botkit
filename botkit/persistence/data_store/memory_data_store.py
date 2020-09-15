from collections import defaultdict
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    AbstractSet,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    AsyncIterator,
    AsyncIterable,
    Coroutine,
    Collection,
    AsyncGenerator,
    Deque,
    Dict,
    List,
    Set,
    FrozenSet,
    NamedTuple,
    Generator,
    cast,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import TypedDict

from haps import SINGLETON_SCOPE, egg, scope

from botkit.future_tgtypes.chat_descriptor import ChatDescriptor
from botkit.future_tgtypes.message_descriptor import MessageDescriptor
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

    async def retrieve_message_data(self, message_descriptor: Optional[MessageDescriptor]):
        if not message_descriptor:
            return None
        return self._data["messages"][message_descriptor]

    async def retrieve_chat_data(self, chat_descriptor: Optional[ChatDescriptor]):
        if not chat_descriptor:
            return None
        return self._data["chats"][chat_descriptor]

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
            chat_descriptor = ChatDescriptor.from_chat_and_user(
                chat, user, context.client.own_user_id
            )
            self._data["chats"][chat_descriptor] = context.chat_state
        if message_descriptor := context.message_descriptor:
            self._data["messages"][message_descriptor] = context.message_state
