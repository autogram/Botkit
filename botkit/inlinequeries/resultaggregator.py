from typing import Iterable

from pyrogram import InlineQuery

from botkit.inlinequeries.inlineresultgenerator import InlineResultGenerator


async def aggregate_results(
    inline_query: InlineQuery, generators: Iterable[InlineResultGenerator]
) -> InlineResultContainer:

    container = InlineResultContainer(inline_query)
    for generator in generators:
        match_result = generator.matches(inline_query)
        if match_result:
            await generator.generate(container, inline_query, match_result)
            break
    return container
