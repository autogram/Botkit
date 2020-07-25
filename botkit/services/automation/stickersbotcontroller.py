import asyncio
from asyncio import Future

from haps import base, egg, inject, Inject
from pyrogram import Message

from botkit.services.automation.stickeroptimizercontroller import StickerOptimizerController
from tgintegration import BotController, InteractionClient


@base
@egg
class StickersBotController(BotController):
    optimizer: StickerOptimizerController = Inject()

    @inject
    def __init__(self, *, client: InteractionClient):
        super().__init__("@StickersBot", client)

    async def list_pack_names(self):
        res = await self.send_command_await("addsticker", num_expected=1)
        return res.keyboard_buttons

    async def add_sticker_to_pack(
        self, message_with_sticker: Message, pack_name: str, emojis: str
    ):
        optimize_task: Future[Message] = asyncio.ensure_future(
            self.optimizer.optimize_image_in_message(message_with_sticker)
        )
        sent_command = await self.send_command_await("addsticker", num_expected=1)
        pressed_button = await sent_command.reply_keyboard.press_button_await(
            pattern=pack_name
        )
        optimized = await optimize_task
        forwarded_msg = await self.forward_messages_await(
            optimized.chat.id, optimized.message_id, num_expected=1
        )
