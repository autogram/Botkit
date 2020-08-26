from typing import *

from botkit.future_tgtypes.user import User


class Message(Protocol):
    text: Optional[str]
    message_id: int
    from_user: Optional[User]
