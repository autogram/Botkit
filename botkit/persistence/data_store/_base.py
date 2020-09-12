from abc import ABC, abstractmethod

from haps import base

from botkit.views.botkit_context import Context


@base
class IDataStore(ABC):
    @abstractmethod
    async def fill_context_data(self, context: Context) -> None:
        pass  # TODO

    @abstractmethod
    async def synchronize_context_data(self, context: Context):
        pass  # TODO
