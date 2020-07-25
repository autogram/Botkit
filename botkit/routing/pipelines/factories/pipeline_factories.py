from typing import Dict, Type

from botkit.routing.pipelines.factories.base import PipelineFactory
from botkit.routing.pipelines.factories.callback_query_pipeline_factory import CallbackQueryPipelineFactory
from botkit.routing.pipelines.factories.message_pipeline_factory import MessagePipelineFactory
from botkit.routing.pipelines.callbacks import CallbackSignature
from botkit.routing.update_types.updatetype import UpdateType


class InlineQueryPipelineFactory(PipelineFactory):
    def create_callback(self) -> CallbackSignature:
        raise NotImplementedError()


class PollPipelineFactory(PipelineFactory):
    def create_callback(self) -> CallbackSignature:
        raise NotImplementedError()


class UserStatusPipelineFactory(PipelineFactory):
    def create_callback(self) -> CallbackSignature:
        raise NotImplementedError()


PIPELINE_FACTORIES: Dict[UpdateType, Type[PipelineFactory]] = {
    UpdateType.message: MessagePipelineFactory,  # one per module
    UpdateType.callback_query: CallbackQueryPipelineFactory,  # one per client
    UpdateType.inline_query: InlineQueryPipelineFactory,  # result builder???
    UpdateType.poll: PollPipelineFactory,
    UpdateType.user_status: UserStatusPipelineFactory,
}
