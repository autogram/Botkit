from commons.coreservices.botautomation.base import BotAutomationBase
from haps import egg, base
from telethon.tl.custom import InlineResults


@base
class WorkingDictBotController(BotAutomationBase):
    username = '@WorkingDictBot'

    async def fetch_word_definition(self, word: str) -> InlineResults:
        return await self.send_inline_query(word)


@egg
def _factory() -> WorkingDictBotController:
    return WorkingDictBotController()
