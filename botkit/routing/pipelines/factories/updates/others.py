from typing import Dict, Type

from pyrogram import CallbackQuery

from botkit.routing.pipelines.factories.base import UpdatePipelineFactory
from botkit.routing.pipelines.factories.steps.custom_handler_step_factory import (
    CustomHandlerStepFactory,
)
from botkit.routing.pipelines.factories.steps.gather_step_factory import GatherStepFactory
from botkit.routing.pipelines.factories.steps.reduce_step_factory import ReduceStepFactory
from botkit.routing.pipelines.factories.steps.send_view_step_factory import (
    CommitRenderedViewStepFactory,
)
from botkit.routing.pipelines.factories.updates.callback_query_pipeline_factory import (
    CallbackQueryPipelineFactory,
)
from botkit.routing.pipelines.factories.updates.message_pipeline_factory import (
    MessagePipelineFactory,
)
from botkit.routing.pipelines.callbacks import HandlerSignature
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient


class InlineQueryPipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.inline_query

    def create_callback(self) -> HandlerSignature:
        raise NotImplementedError()


class PollPipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.poll

    def create_callback(self) -> HandlerSignature:
        raise NotImplementedError()


class UserStatusPipelineFactory(UpdatePipelineFactory):
    @property
    def update_type(self) -> UpdateType:
        return UpdateType.user_status

    def create_callback(self) -> HandlerSignature:
        raise NotImplementedError()


PIPELINE_FACTORIES: Dict[UpdateType, Type[UpdatePipelineFactory]] = {
    UpdateType.message: MessagePipelineFactory,  # one per module
    UpdateType.callback_query: CallbackQueryPipelineFactory,  # one per client
    UpdateType.inline_query: InlineQueryPipelineFactory,  # result builder???
    UpdateType.poll: PollPipelineFactory,
    UpdateType.user_status: UserStatusPipelineFactory,
}
