from typing import Any, Literal, Optional, Tuple, Union

from pydantic.dataclasses import dataclass

from botkit.future_tgtypes.message_descriptor import Chat
from botkit.future_tgtypes.user import User


@dataclass(frozen=True)
class ChatDescriptor:
    type: Literal["private", "bot", "group", "supergroup", "channel"]
    peers: Union[int, Tuple[int, int]]  # will be a tuple if conversation is `private` or `bot`

    @classmethod
    def from_update(cls, update: Any) -> Optional["ChatDescriptor"]:
        if not (chat := update.chat):
            return None
        return cls.from_chat(chat)

    # noinspection PydanticTypeChecker
    @classmethod
    def from_chat_and_user(cls, chat: Chat, user: User, me_id: int) -> "ChatDescriptor":
        type_ = chat.type
        chat_id = chat.id

        if type_ == "private":
            # Add own client user ID into the mix
            peers = tuple(sorted((me_id, user.id)))
            desc = ChatDescriptor(type=type_, peers=peers)
            return desc
        if type_ == "bot":
            peers = tuple(sorted((chat_id, user.id)))
            desc = ChatDescriptor(type=type_, peers=peers)
            return desc

        return ChatDescriptor(type=type_, peers=chat_id)
