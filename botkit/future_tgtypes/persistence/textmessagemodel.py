from pydantic import BaseModel
from pyrogram import Message
from typing import Optional


class TextMessageModel(BaseModel):
    message_id: int
    date: Optional[int] = None
    chat_id: Optional[int] = None  # custom
    from_user_id: Optional[int] = None  # custom
    forward_from_id: Optional[int] = None  # custom
    forward_sender_name: Optional[str] = None
    forward_from_chat_id: Optional[int] = None  # custom
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_date: Optional[int] = None
    reply_to_message_id: Optional[int] = None  # custom
    mentioned: Optional[bool] = None
    empty: Optional[bool] = None
    service: Optional[bool] = None
    # scheduled: Optional[bool] = None
    # from_scheduled: Optional[bool] = None
    media: Optional[bool] = None
    edit_date: Optional[int] = None
    media_group_id: Optional[str] = None
    author_signature: Optional[str] = None
    text: Optional[str] = None  # custom
    text_markdown: Optional[str] = None  # custom
    text_html: Optional[str] = None  # custom
    # audio: Optional[bool] = None
    # document: Optional[bool] = None
    # photo: Optional[bool] = None
    # sticker: Optional[bool] = None
    # animation: Optional["pyrogram.Animation"] = None
    # game: Optional["pyrogram.Game"] = None
    # video: Optional["pyrogram.Video"] = None
    # voice: Optional["pyrogram.Voice"] = None
    # video_note: Optional["pyrogram.VideoNote"] = None
    caption: Optional[str] = None  # custom
    caption_markdown: Optional[str] = None  # custom
    caption_html: Optional[str] = None  # custom
    # contact: Optional["pyrogram.Contact"] = None
    # location: Optional["pyrogram.Location"] = None
    # venue: Optional["pyrogram.Venue"] = None
    web_page: Optional[str] = None
    # poll: Optional["pyrogram.Poll"] = None
    views: Optional[int] = None
    via_bot_id: Optional[int] = None  # custom
    # reply_markup: optional[
    #     union[
    #         pyrogram.inlinekeyboardmarkup,
    #         pyrogram.replykeyboardmarkup,
    #         pyrogram.replykeyboardremove,
    #         pyrogram.forcereply,
    #     ]
    # ] = none

    @classmethod
    def from_message(cls, msg: Message) -> "TextMessageModel":
        if msg.empty:
            raise ValueError("Message is empty.")
        if msg.service:
            raise ValueError("Service messages are invalid text messages.")

        return TextMessageModel(
            message_id=msg.message_id,
            date=msg.created,
            chat_id=msg.chat.id if msg.chat else None,
            from_user_id=msg.from_user.id if msg.from_user else None,
            forward_from_id=msg.forward_from.id if msg.forward_from else None,
            forward_sender_name=msg.forward_sender_name,
            forward_from_chat_id=msg.forward_from_chat.id
            if msg.forward_from_chat
            else None,
            forward_from_message_id=msg.forward_from_message_id,
            forward_signature=msg.forward_signature,
            forward_date=msg.forward_date,
            reply_to_message_id=msg.reply_to_message.message_id
            if msg.reply_to_message
            else None,
            mentioned=msg.mentioned,
            empty=msg.empty,
            service=msg.service,
            media=msg.media,
            edit_date=msg.edit_date,
            media_group_id=msg.media_group_id,
            author_signature=msg.author_signature,
            text=str(msg.text),
            text_markdown=msg.text.markdown if msg.text else None,
            text_html=msg.text.html if msg.text else None,
            caption=str(msg.caption),
            caption_markdown=msg.caption.markdown if msg.caption else None,
            caption_html=msg.caption.html if msg.caption else None,
            web_page=msg.web_page.url if msg.web_page else None,
            views=msg.views,
            via_bot_id=msg.via_bot.id if msg.via_bot else None,
        )
