from typing import Awaitable

from haps import Inject

from botkit.libraries.annotations import IClient
from botkit.persistence.data_store import IDataStore
from botkit.routing.pipelines.factory_types import IPipelineStep
from typing import (
    Any,
    Optional,
)

from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context


class InitializeContextStep(IPipelineStep):
    data_store: IDataStore = Inject()

    def __init__(self, update_type: UpdateType):
        self.update_type = update_type
        self.log = create_logger("context_initializer")

    def create_new_context(self, client, update):
        return Context(client=client, update=update, update_type=self.update_type, view_state=None)

    async def __call__(self, client: IClient, update: Any, context: Optional[Context]) -> Context:
        if not context:
            context = self.create_new_context(client, update)
            self.log.debug("New context created")
        else:
            self.log.debug("Passing on existing context")

        await self.data_store.fill_context_data(context)

        if context.message_state:
            self.log.debug(f"Carrying message_data of type {type(context.message_state)}")
        if context.user_state:
            self.log.debug(f"Carrying user_data of type {type(context.user_state)}")
        if context.chat_state:
            self.log.debug(f"Carrying chat_data of type {type(context.chat_state)}")

        return context
