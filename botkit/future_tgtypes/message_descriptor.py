from typing import Literal, Optional, Protocol, Union, runtime_checkable

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class Chat(Protocol):
    id: int
    type: Literal["private", "bot", "group", "supergroup", "channel"]


@runtime_checkable
class _MessageUpdate(Protocol):
    chat: Chat
    message_id: int


@runtime_checkable
class _CallbackQueryUpdate(Protocol):
    inline_message_id: str


@dataclass(frozen=True)
class MessageDescriptor:
    chat_id: Optional[Union[int, str]]  # will be None for inline messages
    message_id: Union[int, str]
    is_inline: bool
    is_deleted: bool = False  # TODO: implement

    @classmethod
    def from_update(
        cls, update: Union[_MessageUpdate, _CallbackQueryUpdate]
    ) -> "MessageDescriptor":
        if isinstance(update, _MessageUpdate):
            return cls.from_message(update)
        elif isinstance(update, _CallbackQueryUpdate) and update.inline_message_id:
            return MessageDescriptor(
                chat_id=None, message_id=update.inline_message_id, is_inline=True,
            )
        raise ValueError(f"Could not extract a message location from update: {update}")

    @classmethod
    def from_message(cls, message: _MessageUpdate):
        return MessageDescriptor(
            chat_id=message.chat.id, message_id=message.message_id, is_inline=False
        )
