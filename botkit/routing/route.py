import warnings
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, TypeVar, cast

from cached_property import cached_property
from pyrogram.filters import Filter
from pyrogram.handlers import (
    CallbackQueryHandler,
    InlineQueryHandler,
    MessageHandler,
    PollHandler,
    RawUpdateHandler,
    UserStatusHandler,
)
from pyrogram.handlers.handler import Handler

from botkit.agnostic.annotations import HandlerSignature
from botkit.routing.pipelines.executionplan import ExecutionPlan
from botkit.routing.pipelines.filters import UpdateFilterSignature
from botkit.routing.pipelines.updates.update_pipeline_factory import UpdatePipelineFactory
from botkit.routing.triggers import ActionIdType, RouteTriggers
from tgtypes.updatetype import UpdateType

M = TypeVar("M")


@dataclass(frozen=True)
class RouteHandler:
    update_type: UpdateType
    filter: UpdateFilterSignature
    callback: HandlerSignature
    description: str
    scope: Literal["global", "module"] = "module"
    action_id: Optional[ActionIdType] = None
    # TODO: ☝ this is not so nice as it is not set for some instances. Instead maybe go for "unique key in scope"
    #  that is always calculated..?

    @cached_property
    def pyrogram_handler(self) -> Handler:
        return _create_pyrogram_handler(self.callback, self.filter, self.update_type)


class RouteDefinition:
    def __init__(self, triggers: RouteTriggers, plan: ExecutionPlan):
        self.triggers = triggers
        self.plan = plan

    # TODO(lib-agnostic): Move this away
    @cached_property
    def pyrogram_handlers(self) -> List[Handler]:
        return [
            _create_pyrogram_handler(rh.callback, rh.filter, ud_type)
            for ud_type, rh in self.handler_by_update_type.items()
        ]

    @cached_property
    def handler_by_update_type(self) -> Dict[UpdateType, RouteHandler]:
        update_types = self.plan._update_types

        # if not update_types:
        #     # Should never happen if handler is set.
        #     # TODO: can happen with disabled modules
        #     warnings.warn(f"No update types were determined at route initialization.")

        results = {}
        for update_type in update_types:
            factory = UpdatePipelineFactory()
            results[update_type] = RouteHandler(
                update_type=update_type,
                filter=factory.create_update_filter(self.triggers),
                callback=factory.build_callback(self.plan, update_type),
                description=factory.get_description(self.triggers, self.plan, update_type),
                scope="module",  # TODO implement
                action_id=self.triggers.action,
            )

        return results

    @cached_property
    def description(self) -> str:
        return "; ".join([x.description or "" for x in self.handler_by_update_type.values()])


def _create_pyrogram_handler(
    callback: HandlerSignature, update_filter: UpdateFilterSignature, update_type: UpdateType,
) -> Handler:
    assert callback is not None

    # `UpdateFilterSignature` is deliberately compatible with Pyrogram `Filter`
    pyro_filters = cast(Filter, update_filter)

    if update_type == UpdateType.message:
        return MessageHandler(callback=callback, filters=pyro_filters)
    elif update_type == UpdateType.callback_query:
        return CallbackQueryHandler(callback=callback, filters=pyro_filters)
    elif update_type == UpdateType.inline_query:
        return InlineQueryHandler(callback=callback, filters=pyro_filters)
    elif update_type == UpdateType.poll:
        return PollHandler(callback=callback, filters=pyro_filters)
    elif update_type == UpdateType.user_status:
        return UserStatusHandler(callback=callback, filters=pyro_filters)
    elif update_type == UpdateType.raw:
        return RawUpdateHandler(callback=callback)
    else:
        # Should never happen
        raise ValueError(f"Could not find a matching Pyrogram callback class for {update_type}.")
