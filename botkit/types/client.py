from abc import ABC, abstractmethod
from typing import Generic, Iterable, Protocol, TypeVar, Union

from botkit.views.sender_interface import IViewSender, Message


class IdentifiableUser(Protocol):
    id: int
    username: str


User = TypeVar("User", bound=IdentifiableUser)


class IClient(IViewSender[Message], ABC, Generic[Message, User]):
    own_user_id: int

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

    # TODO: mark as @abstractmethod
    async def delete_messages(
        self,
        chat_id: Union[int, str],
        message_ids: Union[int, Message, Iterable[Union[int, Message]]],
        revoke: bool = True,
    ) -> bool:
        ...

    # TODO: mark as @abstractmethod
    async def get_inline_bot_results(self, bot_username, query_text):
        pass
