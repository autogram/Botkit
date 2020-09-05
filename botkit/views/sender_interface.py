from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Union, overload

from botkit.views.rendered_messages import RenderedMessageBase
from botkit.views.views import MediaView, MessageViewBase, StickerView, TextView

Message = TypeVar("Message")


class IViewSender(ABC, Generic[Message]):
    @abstractmethod
    async def send_rendered_message(
        self,
        peer: Union[int, str],
        rendered: RenderedMessageBase,
        reply_to: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @abstractmethod
    async def update_message_with_rendered(
        self,
        peer: Union[int, str],
        message_id: int,
        rendered: RenderedMessageBase,
    ) -> Message:
        ...

    @abstractmethod
    async def update_inline_message_with_rendered(
        self,
        inline_message_id: str,
        rendered: RenderedMessageBase,
    ) -> bool:
        ...

    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: TextView,
        *,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: MediaView,
        *,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: StickerView,
        *,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @abstractmethod
    async def send_view(
        self,
        peer: Union[int, str],
        view: MessageViewBase,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @overload
    async def update_view(
        self, peer: Union[int, str], message: Union[int, Message], view: TextView
    ) -> Message:
        ...

    @overload
    async def update_view(
        self, peer: Union[int, str], message: Union[int, Message], view: MediaView
    ) -> Message:
        ...

    async def update_view(
        self, peer: Union[int, str], message: Union[int, Message], view: MessageViewBase
    ) -> Message:
        ...

    @overload
    async def update_inline_view(self, inline_message_id: str, view: TextView) -> bool:
        ...

    @overload
    async def update_inline_view(self, inline_message_id: str, view: MediaView) -> bool:
        ...

    async def update_inline_view(
        self, inline_message_id: str, view: MessageViewBase
    ) -> bool:
        ...
