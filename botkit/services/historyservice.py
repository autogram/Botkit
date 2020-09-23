from collections import Counter
from typing import (
    Any,
    Awaitable,
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

from haps import SINGLETON_SCOPE, egg, base, scope
from pyrogram import Client
from typing import Callable, Union, AsyncGenerator, cast

from pyrogram.types import Message

from botkit.future_tgtypes.message_identity import MessageIdentity
from botkit.utils.typed_callable import TypedCallable


@base
@egg
@scope(SINGLETON_SCOPE)
class HistoryService:
    def __init__(self, client: Client):
        self.client = client

    async def follow_reply_chain(
        self, from_message: Message, until: Callable[[Message], Union[bool, Awaitable[bool]]],
    ) -> AsyncGenerator[Message, None]:
        # TODO: untested
        Message.__hash__ = lambda x: (x.chat.id << 32) + x.message_id
        until_is_coroutine = TypedCallable(until).is_coroutine

        yield from_message

        while True:
            reply_msg = from_message.reply_to_message
            if not reply_msg or reply_msg.empty:
                return

            if until_is_coroutine:
                is_match = await until(reply_msg)
            else:
                is_match = until(reply_msg)

            if not is_match:
                return

            yield reply_msg

    async def iter_replies_to(
        self, chat_id: Union[int, str], target_message: Union[Message, int], vicinity: int = 500,
    ) -> AsyncGenerator[Message, None]:
        target_message_id: int = (
            target_message if isinstance(target_message, int) else target_message.message_id
        )
        history_gen = self.client.iter_history(
            chat_id, limit=vicinity, offset_id=target_message_id, reverse=True
        )

        # noinspection PyTypeChecker
        async for m in cast(AsyncGenerator[Message, None], history_gen):
            if m.empty:
                continue
            if m.reply_to_message and m.reply_to_message.message_id == target_message_id:
                yield m

    async def get_reply_counts(self, chat_id: Union[int, str], lookback: int = 3000) -> Counter:
        counter: Counter = Counter()

        async for m in cast(
            AsyncGenerator[Message, None], self.client.iter_history(chat_id, limit=lookback),
        ):
            reply_msg = m.reply_to_message
            if reply_msg:
                if reply_msg.empty:
                    continue
                Message.__hash__ = lambda x: (x.chat.id << 32) + x.message_id
                counter.update([reply_msg])

        return counter
