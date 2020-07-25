from typing import List

from pyrogram import InlineQueryResult, InlineQuery


class InlineResultContainer:
    def __init__(self, inline_query: InlineQuery):
        self._inline_query = inline_query

        # TODO: automatic offset calculation
        self.next_offset: str = ""

        self.results: List[InlineQueryResult] = []
        self.maximum_cache_time: int = 300
        self.contains_personal_results: bool = False
        self.requires_gallery: bool = False
        self.switch_pm_text: str = ""
        self.switch_pm_parameter: str = ""

    async def answer(self):
        return await self._inline_query.answer(
            self.results,
            cache_time=self.maximum_cache_time,
            is_gallery=self.requires_gallery,
            is_personal=self.contains_personal_results,
            next_offset=self.next_offset,
            switch_pm_text=self.switch_pm_text,
            switch_pm_parameter=self.switch_pm_parameter,
        )
