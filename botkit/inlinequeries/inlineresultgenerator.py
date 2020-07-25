from abc import ABC

from abc import ABCMeta, abstractmethod
from decouple import config
from logzero import logger

from botkit.inlinequeries.inlineresultcontainer import InlineResultContainer


class InlineResultGenerator(ABC):
    # def matches(self, inline_query: InlineQuery): TODO: move to IoC
    #     return self.context.matches(inline_query.query)

    @abstractmethod
    async def generate_results(
        self, container: InlineResultContainer, user_input: str
    ) -> bool:
        pass

    async def generate(
        self,
        container: InlineResultContainer,
        user_input: str
    ) -> None:

        # user_input = self.context.parse_input(
        #     query=inline_query.query, match_result=match_result
        # ).strip()

        logger.debug(f"Generating results for {self.__class__.__name__}...")
        if user_input:
            logger.debug(user_input)

        if config("DEBUG", cast=bool):
            container.maximum_cache_time = 1

        await self.generate_results(container, user_input)
