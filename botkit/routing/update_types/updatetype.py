from enum import Enum, auto

from boltons.typeutils import classproperty


class UpdateType(Enum):
    raw = auto()
    message = auto()
    callback_query = auto()
    inline_query = auto()
    poll = auto()
    user_status = auto()
    command = auto()

    # noinspection PyMethodParameters
    @classproperty
    def all(cls):
        return [
            cls.raw,
            cls.message,
            cls.callback_query,
            cls.inline_query,
            cls.poll,
            cls.user_status,
        ]
