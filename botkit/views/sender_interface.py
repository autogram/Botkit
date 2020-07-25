from abc import ABC
from typing import Optional, Union, overload

from pyrogram import Message

from botkit.views.views import MediaView, MessageViewBase, StickerView, TextView


class IViewSender(ABC):
    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: TextView,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: MediaView,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @overload
    async def send_view(
        self,
        peer: Union[int, str],
        view: StickerView,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    async def send_view(
        self,
        peer: Union[int, str],
        view: MessageViewBase,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        ...

    @overload
    async def update_view(self, peer: Union[int, str], message: Union[int, Message], view: TextView) -> Message:
        ...

    @overload
    async def update_view(self, peer: Union[int, str], message: Union[int, Message], view: MediaView) -> Message:
        ...

    async def update_view(self, peer: Union[int, str], message: Union[int, Message], view: MessageViewBase) -> Message:
        ...

    @overload
    async def update_inline_view(self, inline_message_id: str, view: TextView) -> bool:
        ...

    @overload
    async def update_inline_view(self, inline_message_id: str, view: MediaView) -> bool:
        ...

    async def update_inline_view(self, inline_message_id: str, view: MessageViewBase) -> bool:
        ...
