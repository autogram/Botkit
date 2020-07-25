from enum import Enum


class UpdateType(Enum):
    raw = 0
    message = 1
    callback_query = 2
    inline_query = 3
    poll = 4
    user_status = 5
