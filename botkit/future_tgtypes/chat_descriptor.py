from typing import Any, Literal, Optional, Tuple, Union

from pydantic.dataclasses import dataclass

from botkit.future_tgtypes.message_descriptor import Chat
from botkit.future_tgtypes.user import User
from botkit.utils.botkit_logging.setup import create_logger

log = create_logger("chat_descriptor")


@dataclass(frozen=True)
class ChatDescriptor:
    type: Literal["private", "bot", "group", "supergroup", "channel"]
    peers: Union[int, Tuple[int, int]]  # will be a tuple if conversation is `private` or `bot`

    # noinspection PydanticTypeChecker
    @classmethod
    def from_chat_and_user(
        cls, chat: Optional[Chat], user: User, client_user_id: int
    ) -> "Optional[ChatDescriptor]":
        if not chat:
            log.warning("No chat found in update. This is most likely due to an inline message.")
            return None
        type_ = chat.type
        chat_id = chat.id

        if type_ == "private":
            # Add own client user ID into the mix
            peers = tuple(sorted((client_user_id, user.id)))
            desc = ChatDescriptor(type=type_, peers=peers)
            return desc
        if type_ == "bot":
            peers = tuple(sorted((chat_id, user.id)))
            desc = ChatDescriptor(type=type_, peers=peers)
            return desc

        return ChatDescriptor(type=type_, peers=chat_id)

    def get_chat_id(self, client_user_id: int) -> int:
        if isinstance(self.peers, int):
            return self.peers

        peers_set = set(self.peers)
        peers_set.remove(client_user_id)

        if len(peers_set) == 1:
            return peers_set.pop()

        raise NotImplementedError(
            "There are some combinations of type, user clients, and bot clients that have not "
            "been considered yet for resolving chat_ids from ChatDescriptors. Please"
            "open an issue on GitHub!"
        )
