from typing import Iterable

from pyrogram.types import InlineQuery

from botkit.inlinequeries.inlineresultcontainer import InlineResultContainer
from botkit.inlinequeries.inlineresultgenerator import InlineResultGenerator


async def aggregate_results(
    inline_query: InlineQuery, generators: Iterable[InlineResultGenerator]
) -> InlineResultContainer:

    container = InlineResultContainer(inline_query)
    for generator in generators:
        await generator.generate(container, "user_input")
    return container
