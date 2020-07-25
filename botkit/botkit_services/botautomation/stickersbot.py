from dataclasses import dataclass
from telethon.events import NewMessage
from telethon.tl.custom import Message

from commons.coreservices.botautomation.base import BotAutomationBase


class StickersBot(BotAutomationBase):
    __username__ = '@Stickers'

    @dataclass
    class State(object):
        addsticker_initialized = False
        sticker_forwarded = False

    state: State = State()

    async def init_addsticker(self, sticker_pack: str):
        wait_event = self.conversation.wait_event(
            NewMessage(incoming=True, chats=[self.__username__], pattern=r'^Alright! Now send .*'),
            timeout=10
        )
        await self.conversation.send_message("/addsticker")
        await self.conversation.send_message(sticker_pack)
        await wait_event

        self.state.addsticker_initialized = True

    async def add_sticker(self, sticker: Message, emojis: str):
        if not self.state.addsticker_initialized:
            raise RuntimeError("Cannot add_for_current_client sticker to pack without initializing first.")

        wait_event = self.conversation.wait_event(
            NewMessage(incoming=True, chats=[self.__username__]),
            timeout=10
        )
        await self.client.forward_messages(self.__username__, [sticker])
        response: NewMessage.Event = await wait_event

        # TODO: error handling
        print(response.message)

        self.state.sticker_forwarded = True

        await self.conversation.send_message(emojis)



