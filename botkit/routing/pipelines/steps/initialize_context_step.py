from typing import Awaitable

from haps import Container, Inject

from botkit.libraries.annotations import IClient
from botkit.persistence.data_store import DataStoreBase
from botkit.routing.pipelines.factory_types import IPipelineStep
from typing import (
    Any,
    Optional,
)

from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context


class InitializeContextStep(IPipelineStep):
    def __init__(self, update_type: UpdateType, data_store: DataStoreBase):
        self.update_type = update_type
        self.data_store = data_store

        self.log = create_logger("context_initializer")

    def create_new_context(self, client, update):
        return Context(client=client, update=update, update_type=self.update_type, view_state=None)

    async def __call__(self, client: IClient, update: Any, context: Optional[Context]) -> Context:
        if not context:
            context = self.create_new_context(client, update)
        else:
            self.log.debug("Passing on existing context")

        await self.data_store.fill_context_data(context)

        if context.message_state:
            self.log.debug(f"Carrying message_state of type {type(context.message_state)}")
        if context.user_state:
            self.log.debug(f"Carrying user_state of type {type(context.user_state)}")
        if context.chat_state:
            self.log.debug(f"Carrying chat_state of type {type(context.chat_state)}")

        return context
