from commons.coreservices.botautomation.base import BotAutomationBase
from haps import base, egg
from telethon.tl.custom import InlineResults
from telethon.tl.types import Document
from typing import Dict, List


@base
class StickerFinderBot(BotAutomationBase):
    __username__ = "@stfi_bot"

    def __init__(self):
        super(StickerFinderBot, self).__init__()

        self.results_cache: Dict[str, InlineResults] = {}
        self.reuse_cache: Dict[str, List[Document]] = {}

    async def search_sticker(self, query) -> Document:
        results = self.reuse_cache.get(query, [])

        if not results:
            results = await self.search_many_stickers(query)

        if not results:
            return None

        res: Document = results[0]

        # Save remaining results in cache
        results.remove(res)
        self.reuse_cache[query] = results

        if not res:
            return None

        return res

    async def search_many_stickers(self, query) -> List[Document]:
        results = self.results_cache.get(query, [])

        if not results:
            results = await self.send_inline_query(query)

        if not results:
            return []

        self.results_cache[query] = results

        return [x.document for x in results]


@egg
def stfi_factory() -> StickerFinderBot:
    return StickerFinderBot()
