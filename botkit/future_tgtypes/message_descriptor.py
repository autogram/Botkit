from typing import Optional, Protocol, Union, runtime_checkable

from pydantic import BaseModel


class _Chat(Protocol):
    id: int


@runtime_checkable
class _MessageUpdate(Protocol):
    chat: _Chat
    message_id: int


@runtime_checkable
class _CallbackQueryUpdate(Protocol):
    chat: _Chat
    inline_message_id: str


class MessageDescriptor(BaseModel):
    chat_id: Union[int, str]
    message_id: int
    is_inline: bool
    is_deleted: bool = False  # TODO: implement

    @classmethod
    def from_update(cls, update: Union[_MessageUpdate, _CallbackQueryUpdate]) -> "MessageDescriptor":
        if isinstance(update, _MessageUpdate):
            return cls.from_message(update)
        elif isinstance(update, _CallbackQueryUpdate) and update.inline_message_id:
            return MessageDescriptor(chat_id=update.chat.id, message_id=update.inline_message_id, is_inline=True)
        raise ValueError(f"Could not extract a message location from update: {update}")

    @classmethod
    def from_message(cls, message: _MessageUpdate):
        return MessageDescriptor(chat_id=message.chat.id, message_id=message.message_id, is_inline=False)
