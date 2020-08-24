from typing import *


class Message(Protocol):
    text: Optional[str]
    message_id: int
