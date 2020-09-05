from typing import Dict, Type

from botkit.libraries.annotations import HandlerSignature
from botkit.routing.pipelines.updates import CallbackQueryPipelineFactory
from botkit.routing.pipelines.updates import MessagePipelineFactory
from botkit.routing.pipelines.updates.update_pipeline_factory import (
    UpdatePipelineFactory,
)
from botkit.routing.update_types.updatetype import UpdateType


class InlineQueryPipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.inline_query

    def create_unified_callback(self) -> HandlerSignature:
        raise NotImplementedError()


class PollPipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.poll

    def create_unified_callback(self) -> HandlerSignature:
        raise NotImplementedError()


class UserStatusPipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.user_status

    def create_unified_callback(self) -> HandlerSignature:
        raise NotImplementedError()


PIPELINE_FACTORIES: Dict[UpdateType, Type[UpdatePipelineFactory]] = {
    UpdateType.message: MessagePipelineFactory,  # one per module
    UpdateType.callback_query: CallbackQueryPipelineFactory,  # one per client
    UpdateType.inline_query: InlineQueryPipelineFactory,  # result builder???
    UpdateType.poll: PollPipelineFactory,
    UpdateType.user_status: UserStatusPipelineFactory,
}
