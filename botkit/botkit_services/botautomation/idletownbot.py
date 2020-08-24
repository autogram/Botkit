import asyncio
from commons.coreservices.botautomation.base import BotAutomationBase
from telethon.events import NewMessage
from telethon.tl.custom import Message
from typing import Dict, Union


class IdleTownBotBase(BotAutomationBase):

    __username__ = "@IdleTownBot"

    @staticmethod
    async def sleep():
        await asyncio.sleep(1.9)

    async def get_buttons(self) -> Dict[str, str]:
        return get_buttons(await self.conversation.get_response())

    async def get_text(self) -> str:
        return (await self.conversation.get_response()).text

    async def execute_single_run(self):
        # Setup
        await self.client.clear_chat()
        await asyncio.sleep(2)

        start: Message = await self.conversation.send_message("/start")
        main_buttons = await self.get_buttons()
        await self.sleep()

        # Get World Exp if possible
        if "worldexp" in main_buttons:
            await self.conversation.send_message(main_buttons["worldexp"])
            worldexp = await self.get_buttons()
            await self.sleep()

            await self.conversation.send_message(worldexp["claimx1"])
            confirm_buttons = await self.get_buttons()
            await self.sleep()

            await self.conversation.send_message(confirm_buttons["yes"])
            await self.sleep()

        # Construct buildings
        await self.conversation.send_message(main_buttons["buildings"])
        build_buttons = await self.get_buttons()
        await self.sleep()

        for building in ["lumbermill", "goldmine", "armory", "smithy"]:
            response_text = ""
            while "you don't have enough" not in response_text.lower():
                await self.conversation.send_message(build_buttons[building])
                response_text = await self.get_text()
                await self.sleep()

        # Upgrade Hero Equipment
        await self.conversation.send_message(main_buttons["hero"])
        hero = await self.get_buttons()
        await self.sleep()

        await self.conversation.send_message(hero["equipment"])
        equip_buttons = await self.get_buttons()
        await self.sleep()

        # For every possible equipment, upgrade it until there are not enough resources left
        for equip in (b for k, b in equip_buttons.items() if "up" in k):
            while True:
                await self.conversation.send_message(equip)
                response_text = await self.get_text()
                await self.sleep()
                if "you don't have enough" in response_text.lower():
                    break

        # Attack Player
        await self.conversation.send_message(main_buttons["battle"])
        battle = await self.get_buttons()
        await self.sleep()

        await self.conversation.send_message(battle["arena"])
        arena = await self.get_buttons()
        await self.sleep()

        await self.conversation.send_message(arena["normalmatch"])
        normal_match = await self.get_buttons()
        await self.sleep()

        if "fight" in normal_match:
            await self.conversation.send_message(normal_match["fight"])
            fight = await self.get_buttons()
            await self.sleep()

        # Attack Boss
        await self.conversation.send_message(battle["bosses"])
        bosses = await self.get_buttons()
        await self.sleep()
        if "attackmax" in bosses:
            await self.conversation.send_message(bosses["attackmax"])
            await self.sleep()


def ascii_chars(text):
    return "".join(x for x in text if str.isalpha(x) or str.isdigit(x)).strip()


def get_buttons(event_or_message: Union[NewMessage.Event, Message]):
    """
    Helper function to create a dictionary for easy access to keyboard inline_buttons
    """
    if isinstance(event_or_message, NewMessage.Event):
        message = event_or_message.message_descriptor
    else:
        message = event_or_message

    all_buttons = []
    for row in message.reply_markup.rows:
        all_buttons += map(lambda b: b.text, row.buttons)
    res = {ascii_chars(b).lower(): b for b in all_buttons}
    return res
