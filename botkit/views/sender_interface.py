from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Union, overload

from botkit.views.rendered_messages import RenderedMessageBase
from botkit.views.views import MediaView, MessageViewBase, StickerView, TextView

view_sender_interface = TypeVar("view_sender_interface")


class IViewSender(ABC, Generic[view_sender_interface]):
    @abstractmethod
    async def send_rendered_message(
        self,
        peer: Union[int, str],
        rendered: RenderedMessageBase,
        reply_to: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> view_sender_interface:
        ...

    @abstractmethod
    async def update_message_with_rendered(
        self, peer: Union[int, str], message_id: int, rendered: RenderedMessageBase,
    ) -> view_sender_interface:
        ...

    @abstractmethod
    async def update_inline_message_with_rendered(
        self, inline_message_id: str, rendered: RenderedMessageBase,
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
    ) -> view_sender_interface:
        ...

    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: MediaView,
        *,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> view_sender_interface:
        ...

    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: StickerView,
        *,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> view_sender_interface:
        ...

    @abstractmethod
    async def send_view(
        self,
        peer: Union[int, str],
        view: MessageViewBase,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> view_sender_interface:
        ...

    @overload
    async def update_view(
        self, peer: Union[int, str], message: Union[int, view_sender_interface], view: TextView
    ) -> view_sender_interface:
        ...

    @overload
    async def update_view(
        self, peer: Union[int, str], message: Union[int, view_sender_interface], view: MediaView
    ) -> view_sender_interface:
        ...

    async def update_view(
        self,
        peer: Union[int, str],
        message: Union[int, view_sender_interface],
        view: MessageViewBase,
    ) -> view_sender_interface:
        ...

    @overload
    async def update_inline_view(self, inline_message_id: str, view: TextView) -> bool:
        ...

    @overload
    async def update_inline_view(self, inline_message_id: str, view: MediaView) -> bool:
        ...

    async def update_inline_view(self, inline_message_id: str, view: MessageViewBase) -> bool:
        ...
