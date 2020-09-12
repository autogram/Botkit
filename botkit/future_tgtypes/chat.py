from typing import Any, Literal, Protocol, Union


class Chat(Protocol):
    id: int
    type: Union[Literal["private", "bot"], str]  # TODO: fill
