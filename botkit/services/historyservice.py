from collections import Counter

from haps import SINGLETON_SCOPE, egg, base, scope
from pyrogram import Client
from typing import Union, AsyncGenerator, cast

from pyrogram.types import Message


@base
@egg
@scope(SINGLETON_SCOPE)
class HistoryService:
    def __init__(self, client: Client):
        self.client = client

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
