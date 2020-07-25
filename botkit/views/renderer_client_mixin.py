from pyrogram import Client
from pyrogram import Message
from typing import *

from botkit.views.base import InlineResultViewBase
from botkit.views.sender_interface import IViewSender
from botkit.views.views import (
    MessageViewBase,
    TextView,
    MediaView,
    StickerView,
)


class PyroRendererClientMixin(Client, IViewSender):
    async def send_view(
        self,
        peer: Union[int, str],
        view,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        rendered = view.render()

        if isinstance(view, TextView):
            return await self.send_message(
                peer,
                text=rendered.text,
                parse_mode=rendered.parse_mode,
                disable_web_page_preview=rendered.disable_web_page_preview,
                reply_markup=rendered.inline_keyboard_markup,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
            )
        elif isinstance(view, MediaView):
            return await self.send_photo(
                peer,
                photo=rendered.photo,
                caption=rendered.caption,
                parse_mode=rendered.parse_mode,
                reply_markup=rendered.inline_keyboard_markup,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
            )
        elif isinstance(view, StickerView):
            return await self.send_sticker(
                peer,
                sticker=rendered.sticker,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
                reply_markup=rendered.reply_markup,
            )
        else:
            raise ValueError(f"No suitable send method found for {type(view)}!")

    async def update_view(
        self, peer: Union[int, str], message: Union[int, Message], view: InlineResultViewBase
    ) -> Message:
        rendered = view.render()

        message = message.message_id if isinstance(message, Message) else int(message)

        if isinstance(view, TextView):
            return await self.edit_message_text(
                peer,
                message,
                text=rendered.text,
                parse_mode=rendered.parse_mode,
                disable_web_page_preview=rendered.disable_web_page_preview,
                reply_markup=rendered.inline_keyboard_markup,
            )
        elif isinstance(view, MediaView):
            # TODO: implement in pyro
            # await self.edit_message_media(
            #     peer,
            #     messages,
            #     photo=rendered.photo,
            #     reply_markup=rendered.inline_keyboard_markup,
            # )
            return await self.edit_message_caption(
                peer,
                message,
                caption=rendered.caption,
                parse_mode=rendered.parse_mode,
                reply_markup=rendered.inline_keyboard_markup,
            )
        elif isinstance(view, ReplyTextView):
            return await self.edit_message_text(
                peer,
                message,
                text=rendered.text,
                parse_mode=rendered.parse_mode,
                disable_web_page_preview=rendered.disable_web_page_preview,
                reply_markup=rendered.reply_markup,
            )
        else:
            raise ValueError(f"No suitable send method found for {type(view)}!")

    async def update_inline_view(self, inline_message_id: str, view: MessageViewBase) -> bool:
        rendered = view.render()

        if isinstance(view, TextView):
            return await self.edit_inline_text(
                inline_message_id=inline_message_id,
                text=rendered.text,
                parse_mode=rendered.parse_mode,
                disable_web_page_preview=rendered.disable_web_page_preview,
                reply_markup=rendered.inline_keyboard_markup,
            )
        elif isinstance(view, MediaView):
            return await self.edit_inline_media(
                inline_message_id=inline_message_id,
                media=rendered.media,
                reply_markup=rendered.inline_keyboard_markup,
            )
            # await self.edit_inline_caption(
            #     inline_message_id=inline_message_id,
            #     caption=rendered.caption,
            #     parse_mode=rendered.parse_mode,
            #     reply_markup=rendered.inline_keyboard_markup,
            # )
        else:
            raise ValueError(f"No suitable send method found for {type(view)}!")
