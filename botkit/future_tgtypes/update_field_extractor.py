import re
from dataclasses import dataclass
from typing import *

import pyrogram
from pyrogram import Update

from botkit.future_tgtypes.chat import Chat
from botkit.future_tgtypes.message import Message
from botkit.future_tgtypes.message_descriptor import MessageDescriptor


@dataclass
class UpdateFieldExtractor:  # TODO: implement properly
    update: Update

    @property
    def chat(self) -> Optional[Chat]:
        if isinstance(self.update, pyrogram.Message):
            return self.update.chat
        return None

    @property
    def message(self) -> Optional[MessageDescriptor]:
        return MessageDescriptor.from_update(self.update)

    @property
    def message_text(self) -> Optional[str]:
        if hasattr(self.update, "text"):
            return self.update.text

    @property
    def command_name(self) -> Optional[str]:
        if hasattr(self.update, "command"):  # Pyrogram
            return self.update.command[0]

    @property
    def command_args(self) -> Optional[List[str]]:
        if hasattr(self.update, "command"):  # Pyrogram
            return self.update.command[1:]

    @property
    def command_arg_str(self) -> Optional[str]:
        return " ".join(self.command_args) if self.command_args else None

    @property
    def replied_to_message(self) -> Optional[Message]:
        # TODO: turn into protocols
        if isinstance(self.update, pyrogram.Message):
            return self.update.reply_to_message

    @property
    def matches(self) -> Optional[List[re.Match]]:
        if hasattr(self.update, "matches"):
            return self.update.matches
