import asyncio

from loguru._logger import Logger

from botkit.agnostic.annotations import IClient
from botkit.botkit_context import Context
from botkit.persistence.data_store import DataStoreBase
from botkit.routing.pipelines.factory_types import IPipelineStep
from typing import (
    Any,
    Optional,
)

from tgtypes.models import Update
from tgtypes.updatetype import UpdateType
from botkit.utils.botkit_logging.setup import create_logger
from injector import Binder, Provider, inject, provider, Module, Injector, multiprovider, singleton


class ContextInitializer:
    @inject
    def __init__(self, client: IClient, data_store: DataStoreBase, log: Logger):
        self.client = client
        self.data_store = data_store
        self.log = log

    async def __call__(self, event_type: UpdateType, event_data: Update) -> Context:
        update = event_data

        context = Context(
            client=self.client,
            update=update,
            update_type=UpdateType.message,  # TODO: hardcoded
            view_state=None,
        )

        await self.fill_context_data(context)

        if context.message_state:
            self.log.debug(f"Carrying message_state of type {type(context.message_state)}")
        if context.user_state:
            self.log.debug(f"Carrying user_state of type {type(context.user_state)}")
        if context.chat_state:
            self.log.debug(f"Carrying chat_state of type {type(context.chat_state)}")

        return context

    async def fill_context_data(self, context: Context):
        tasks = [
            self.data_store.retrieve_user_data(context.user_id),
            self.data_store.retrieve_chat_data(context.chat_identity),
            self.data_store.retrieve_message_data(context.message_identity),
        ]
        res = await asyncio.gather(*tasks)

        user_data, chat_data, message_data = res

        context.user_state = user_data
        context.chat_state = chat_data
        context.message_state = message_data
