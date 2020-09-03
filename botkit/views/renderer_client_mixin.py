from abc import ABC
from typing import *

try:
    # TODO: Turn this into a contextmanager, `with lib_check('Pyrogram'): import ...`
    # noinspection PyPackageRequirements
    from pyrogram import Client
    from pyrogram.types import Message, User
except ImportError as e:
    raise ImportError(
        "The Pyrogram library does not seem to be installed, so using Botkit in Pyrogram flavor is not possible. "
    ) from e

from botkit.types.client import IClient
from botkit.views.base import InlineResultViewBase
from botkit.views.types import TState
from botkit.views.rendered_messages import (
    RenderedMediaMessage,
    RenderedMessageBase,
    RenderedStickerMessage,
    RenderedTextMessage,
)
from botkit.views.functional_views import ViewRenderFuncSignature
from botkit.views.views import MessageViewBase


class PyroRendererClientMixin(Client, IClient[Message, User], ABC):
    async def send_rendered_message(
        self,
        peer: Union[int, str],
        rendered: RenderedMessageBase,
        reply_to: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:
        if isinstance(rendered, RenderedTextMessage):
            return await self.send_message(
                peer,
                text=rendered.text,
                parse_mode=rendered.parse_mode,
                disable_web_page_preview=rendered.disable_web_page_preview,
                reply_markup=rendered.inline_keyboard_markup,
                reply_to_message_id=reply_to,
                schedule_date=schedule_date,
            )
        elif isinstance(rendered, RenderedMediaMessage):
            # TODO: differentiate between the different media types
            return await self.send_photo(
                peer,
                photo=rendered.media,  # TODO: Test this. Not sure if `media` actually contains the photo.
                caption=rendered.caption,
                parse_mode=rendered.parse_mode,
                reply_markup=rendered.inline_keyboard_markup,
                reply_to_message_id=reply_to,
                schedule_date=schedule_date,
            )
        elif isinstance(rendered, RenderedStickerMessage):
            return await self.send_sticker(
                peer,
                sticker=rendered.sticker,
                reply_to_message_id=reply_to,
                schedule_date=schedule_date,
                reply_markup=rendered.reply_markup,
            )
        else:
            raise NotImplementedError(
                f"No suitable `send_*` method found for rendered message '" f"{rendered}'."
            )

    async def update_message_with_rendered(
        self, peer: Union[int, str], message_id: int, rendered: RenderedMessageBase
    ) -> Message:
        if isinstance(rendered, RenderedTextMessage):
            return await self.edit_message_text(
                peer,
                message_id,
                text=rendered.text,
                parse_mode=rendered.parse_mode,
                disable_web_page_preview=rendered.disable_web_page_preview,
                reply_markup=rendered.inline_keyboard_markup,
            )
        elif isinstance(rendered, RenderedMediaMessage):
            # TODO: implement in pyro
            # await self.edit_message_media(
            #     peer,
            #     messages,
            #     photo=rendered.photo,
            #     reply_markup=rendered.inline_keyboard_markup,
            # )
            return await self.edit_message_caption(
                peer,
                message_id,
                caption=rendered.caption,
                parse_mode=rendered.parse_mode,
                reply_markup=rendered.inline_keyboard_markup,
            )
        # elif isinstance(view, ReplyTextView):
        #     return await self.edit_message_text(
        #         peer,
        #         message,
        #         text=rendered_message.text,
        #         parse_mode=rendered_message.parse_mode,
        #         disable_web_page_preview=rendered_message.disable_web_page_preview,
        #         reply_markup=rendered_message.reply_markup,
        #     )
        else:
            raise NotImplementedError(f"No suitable send method found for {rendered}!")

    async def update_inline_message_with_rendered(
        self, inline_message_id: str, rendered: RenderedMessageBase
    ) -> bool:
        if isinstance(rendered, RenderedTextMessage):
            return await self.edit_inline_text(
                inline_message_id=inline_message_id,
                text=rendered.text,
                parse_mode=rendered.parse_mode,
                disable_web_page_preview=rendered.disable_web_page_preview,
                reply_markup=rendered.inline_keyboard_markup,
            )
        elif isinstance(rendered, RenderedMediaMessage):
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
            raise NotImplementedError(f"No suitable send method found for {rendered}!")

    async def send_view(
        self,
        peer: Union[int, str],
        view: Union[MessageViewBase, ViewRenderFuncSignature],
        state: Optional[TState] = None,
        reply_to_message_id: Optional[int] = None,
        schedule_date: Optional[int] = None,
    ) -> Message:

        rendered = view.render()

        return await self.send_rendered_message(
            peer=peer,
            rendered=rendered,
            reply_to=reply_to_message_id,
            schedule_date=schedule_date,
        )

    async def update_view(
        self, peer: Union[int, str], message_id: Union[int, Message], view: InlineResultViewBase
    ) -> Message:
        rendered = view.render()

        message_id = message_id.message_id if isinstance(message_id, Message) else int(message_id)

        return await self.update_message_with_rendered(
            peer=peer, message_id=message_id, rendered=rendered
        )

    async def update_inline_view(self, inline_message_id: str, view: MessageViewBase) -> bool:
        rendered = view.render()

        return await self.update_inline_message_with_rendered(
            inline_message_id=inline_message_id, rendered=rendered
        )
