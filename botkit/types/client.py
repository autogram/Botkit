from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, Protocol, TypeVar, Union

from botkit.views.sender_interface import IViewSender, Message


class IdentifiableUser(Protocol):
    id: int
    username: str


User = TypeVar("User", bound=IdentifiableUser)


class IClient(IViewSender[Message], ABC, Generic[Message, User]):
    @property
    @abstractmethod
    def me_user_id(self) -> int:
        ...

    @property
    @abstractmethod
    def is_bot(self) -> bool:
        ...

    @property
    @abstractmethod
    def is_user(self) -> bool:
        ...

    @abstractmethod
    async def get_me(self) -> IdentifiableUser:
        ...

    # @abstractmethod
    # async def delete_messages(
    #     self,
    #     chat_id: Union[int, str],
    #     message_ids: Union[int, Message, Iterable[Union[int, Message]]],
    #     revoke: bool = True,
    # ) -> bool:
    #     ...
