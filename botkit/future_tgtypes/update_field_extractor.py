import re
import traceback
from dataclasses import dataclass
from typing import *

import pyrogram.types
from pyrogram.types import Update

from botkit.future_tgtypes.chat import Chat
from botkit.future_tgtypes.identities.chat_identity import ChatIdentity
from botkit.future_tgtypes.message import Message
from botkit.future_tgtypes.identities.message_identity import MessageIdentity
from botkit.tghelpers.entities.message_entities import (
    MessageEntityType,
    ParsedEntity,
    parse_entities,
)

if TYPE_CHECKING:
    from botkit.clients.client import IClient


@dataclass
class UpdateFieldExtractor:
    update: Update
    client: Union["IClient", Any]

    @property
    def chat(self) -> Optional[Chat]:
        if hasattr(self.update, "chat"):
            return self.update.chat
        if message := getattr(self.update, "message", None):
            return getattr(message, "chat", None)
        return None

    @property
    def chat_identity(self) -> Optional[ChatIdentity]:
        return ChatIdentity.from_chat_and_user(self.chat, self.user, self.client.own_user_id)

    @property
    def user(self) -> Optional[Chat]:
        if isinstance(self.update, pyrogram.types.Message):
            return self.update.from_user
        return None

    @property
    def chat_id(self) -> Optional[int]:
        return chat.id if (chat := self.chat) else None

    @property
    def user_id(self) -> int:
        return user.id if (user := self.user) else None

    @property
    def message_identity(self) -> Optional[MessageIdentity]:
        return MessageIdentity.from_update(self.update)

    @property
    def message_id(self) -> Optional[Union[int, str]]:
        return descriptor.message_id if (descriptor := self.message_identity) else None

    @property
    def message_text(self) -> Optional[str]:
        if hasattr(self.update, "text"):
            return self.update.text

    @property
    def command_name(self) -> Optional[str]:
        """
        Returns the name of the command without the leading slash or `None` if the update is not a command.
        """
        if hasattr(self.update, "command"):  # Pyrogram
            return self.update.command[0]

    @property
    def command_args(self) -> Optional[List[str]]:
        if hasattr(self.update, "command"):  # Pyrogram
            if len(self.update.command) == 1:
                return []
            return self.update.command[1:]

    @property
    def command_arg_str(self) -> Optional[str]:
        """
        Returns everything after the /command as a string.
        """
        return " ".join(self.command_args) if self.command_args else None

    @property
    def replied_to_message(self) -> Optional[Message]:
        # TODO: turn into protocols
        if isinstance(self.update, pyrogram.types.Message):
            return self.update.reply_to_message

    @property
    def replied_to_message_text(self) -> Optional[str]:
        if isinstance(self.update, pyrogram.types.Message):
            if replied_to := self.update.reply_to_message:
                return replied_to.text
        return None

    quoted = replied_to_message
    quoted_text = replied_to_message_text

    @property
    def replied_to_message_id(self) -> Optional[int]:
        return reply_msg.message_id if (reply_msg := self.replied_to_message) else None

    @property
    def command_args_or_quote(self) -> Optional[str]:
        """ Prefers the command arguments over the replied-to message text, or None if neither is present. """
        return self.command_arg_str or self.replied_to_message_text

    @property
    def matches(self) -> Optional[List[re.Match]]:
        if hasattr(self.update, "matches"):
            return self.update.matches

    @property
    def entities(self) -> List[ParsedEntity]:
        try:
            # noinspection PydanticTypeChecker
            return parse_entities(self.update)
        except Exception as ex:
            traceback.print_exc(ex)
            return []

    def filter_entities(
        self, only: Union[List[MessageEntityType], MessageEntityType]
    ) -> List[ParsedEntity]:
        try:
            # noinspection PydanticTypeChecker
            return parse_entities(self.update, types=only)
        except Exception as ex:
            traceback.print_exc(ex)
            return []
