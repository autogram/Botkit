import traceback
from asyncio import Event
from contextlib import asynccontextmanager
from uuid import uuid4

from app.clients.botclient import BotClient
from app.clients.userclient import UserClient
from haps import INSTANCE_SCOPE, inject
from logzero import logger as log
from pyrogram import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryHandler,
    Message,
    InlineQueryResultPhoto,
    MessageHandler,
    Filters,
    Photo,
)
from pyrogram.api.types.messages import BotResults
from pyrogram.client.filters.filters import create
from pyrogram.client.handlers.handler import Handler
from typing import Union, Optional, AsyncIterator

from botkit.botkit_services.services import service
from botkit.inlinequeries.inlineresultgenerator import InlineResultGenerator
from botkit.views.base import RenderedMessage, InlineResultViewBase


@service(scope=INSTANCE_SCOPE)
class CompanionBotService:
    @inject
    def __init__(self, user_client: UserClient, bot_client: BotClient):
        self.user_client = user_client
        self.bot_client = bot_client

    async def one_time_inline_results(
        self,
        query: str,
        results_generator: InlineResultGenerator,
        reply_to: Union[int, str] = None,
        silent: bool = False,
        hide_via: bool = False,
    ):
        user_client_id = (await self.user_client.get_me()).id
        bot_username = (await self.bot_client.get_me()).username

        query_text = "henlo"

        async def answer_inline_query(client: BotClient, query: InlineQuery):
            rendered: RenderedMessage = view.render()

            result = InlineQueryResultArticle(
                title="sent via userbot",
                input_message_content=InputTextMessageContent(
                    message_text=rendered.text,
                    parse_mode=rendered.parse_mode,
                    disable_web_page_preview=rendered.disable_web_page_preview,
                ),
                id=query.id,
                reply_markup=rendered.inline_keyboard_markup,
                url=None,
                description=None,
                thumb_url=None,
            )

            await self.bot_client.answer_inline_query(
                query.id, results=[result], cache_time=0
            )

        inline_id_filter = create(lambda _, ilq: ilq.query == query_text, "QueryFilter")

        group = -99
        dispatcher = self.bot_client.dispatcher
        if group not in dispatcher.groups:
            dispatcher.groups[group] = []

        handler = InlineQueryHandler(answer_inline_query, inline_id_filter)
        dispatcher.groups[group].append(handler)

        try:
            # Fetch inline results as user
            bot_results: BotResults = await self.user_client.get_inline_bot_results(
                bot_username, query_text
            )
            if not bot_results:
                raise RuntimeError(
                    "Could not fetch any inline query results from companionbot."
                )

            # Send result as user
            return await self.user_client.send_inline_bot_result(
                chat_id,
                query_id=bot_results.query_id,
                result_id=bot_results.results[0].id,
                disable_notification=silent,
                reply_to_message_id=reply_to,
                hide_via=hide_via,
            )
        except (AttributeError, TimeoutError):
            log.error("Bot did not respond.")
        finally:
            self.bot_client.remove_handler(handler, group)

    async def send_view_via(
        self,
        chat_id: Union[int, str],
        view: InlineResultViewBase,
        reply_to=None,
        silent: bool = False,
        hide_via: bool = False,
    ) -> Message:
        bot_username = (await self.bot_client.get_me()).username

        query_text = str(uuid4())

        async def answer_inline_query(client: BotClient, query: InlineQuery):
            rendered: RenderedMessage = view.render()

            if rendered.media:
                result = InlineQueryResultPhoto(
                    photo_url=rendered.media,
                    thumb_url=rendered.thumb_url,
                    id=query.id,
                    title="sent via userbot",
                    description=rendered.description,
                    caption=rendered.caption,
                    parse_mode=rendered.parse_mode,
                    reply_markup=rendered.inline_keyboard_markup,
                    input_message_content=None,
                )
            else:
                result = InlineQueryResultArticle(
                    title="sent via userbot",
                    input_message_content=InputTextMessageContent(
                        message_text=rendered.text,
                        parse_mode=rendered.parse_mode,
                        disable_web_page_preview=rendered.disable_web_page_preview,
                    ),
                    id=query.id,
                    reply_markup=rendered.inline_keyboard_markup,
                    url=None,
                    description=None,
                    thumb_url=None,
                )

            # noinspection PyTypeChecker
            await self.bot_client.answer_inline_query(
                query.id, results=[result], cache_time=1
            )

        inline_id_filter = create(lambda _, ilq: ilq.query == query_text, "QueryFilter")

        handler = InlineQueryHandler(answer_inline_query, inline_id_filter)

        async with self.add_handler(handler):
            try:
                # Fetch inline results as user
                bot_results: BotResults = await self.user_client.get_inline_bot_results(
                    bot_username, query_text
                )
                if not bot_results:
                    raise RuntimeError(
                        "Could not fetch any inline query results from companionbot."
                    )

                try:
                    # TODO: some bug..
                    bot_results.results[0].id
                except:
                    traceback.print_exc()
                    print("Results: ", bot_results.results)
                    print("Returning!!")
                    return

                # Send result as user
                return await self.user_client.send_inline_bot_result(
                    chat_id,
                    query_id=bot_results.query_id,
                    result_id=bot_results.results[0].id,
                    disable_notification=silent,
                    reply_to_message_id=reply_to,
                    hide_via=hide_via,
                )
            except (AttributeError, TimeoutError):
                log.error("Bot did not respond.")

    @asynccontextmanager
    async def add_handler(self, handler: Handler) -> AsyncIterator[None]:
        group = -99
        dispatcher = self.bot_client.dispatcher

        async with dispatcher.locks_list[-1]:
            if group not in dispatcher.groups:
                dispatcher.groups[group] = []
            dispatcher.groups[group].append(handler)

        yield

        async with dispatcher.locks_list[-1]:
            self.bot_client.remove_handler(handler, group)

    async def transfer_message(self, user_message: Message) -> Message:
        recorded_msg = RecordedMessageContainer()

        async def record_message(_, message: Message):
            recorded_msg.set_value(message)
            await message.delete()

        async with self.add_handler(
            MessageHandler(
                record_message,
                filters=Filters.media
                & Filters.chat(user_message.from_user.id)
                & Filters.forwarded,
            )
        ):
            await self.user_client.forward_messages(
                (await self.bot_client.get_me()).id,
                from_chat_id=user_message.chat.id,
                message_ids=[user_message.message_id],
                disable_notification=True,
            )
            await recorded_msg.wait()

        return recorded_msg.recorded_message

    async def make_photo_known(self, photo: str) -> Photo:
        recorded_msg = RecordedMessageContainer()
        user_id = (await self.user_client.get_me()).id
        bot_id = (await self.bot_client.get_me()).id

        async def record_message(_, message: Message):
            recorded_msg.set_value(message)
            await message.delete()

        async with self.add_handler(
            MessageHandler(
                record_message, filters=Filters.photo & Filters.chat(user_id)
            )
        ):
            await self.user_client.send_photo(bot_id, photo=photo)
            await recorded_msg.wait()

        return recorded_msg.recorded_message.photo


class RecordedMessageContainer:
    def __init__(self):
        self.recorded_message: Optional[Message] = None
        self.message_received_event = Event()

    def set_value(self, message: Message):
        if self.recorded_message is not None:
            return
        self.recorded_message = message
        self.message_received_event.set()

    async def wait(self):
        await self.message_received_event.wait()
