import warnings

from haps import base, egg, inject
from pyrogram import Message

from tgintegration import BotController, InteractionClient


@base
@egg
class StickerOptimizerController(BotController):
    @inject
    def __init__(self, *, client: InteractionClient):
        super().__init__("@StickerOptimizerBot", client, max_wait_response=5)

    async def optimize_image_in_message(self, message: Message) -> Message:
        res = await self.client.forward_messages_await(
            self.peer_id, message.chat.id, [message], num_expected=1
        )
        message_with_document = res[0]
        if (
            message_with_document.caption
            and "WARNING!" in message_with_document.caption
        ):
            warnings.warn(message_with_document.caption)
        return message_with_document