from datetime import datetime
from typing import Optional

import pytz

from pyrogram.types import Message


def get_message_date(message: Message, including_edits: bool = True) -> datetime:
    if message is None:
        raise ValueError("view_sender_interface cannot be None.")

    if message.edit_date and including_edits:
        return timestamp_to_datetime(message.edit_date)

    if message.date:
        return timestamp_to_datetime(message.date)

    raise ValueError("No date found in message", message)


def timestamp_to_datetime(timestamp: Optional[int]) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=pytz.UTC)
