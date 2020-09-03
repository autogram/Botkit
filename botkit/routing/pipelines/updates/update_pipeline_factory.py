import inspect
import traceback
from abc import ABC, abstractmethod
from logging import Logger
from typing import Awaitable, cast

import logzero
from pyrogram.types import Update
from unsync import Unfuture, unsync

from botkit.libraries.annotations import HandlerSignature
from botkit.routing.pipelines.execution_plan import ExecutionPlan
from botkit.routing.pipelines.filters import UpdateFilterSignature
from botkit.routing.triggers import RouteTriggers
from botkit.routing.update_types.updatetype import UpdateType
from botkit.types.client import IClient


class UpdatePipelineFactory(ABC):
    def __init__(self, triggers: RouteTriggers, plan: ExecutionPlan):
        self.triggers = triggers
        self.plan = plan

    @property
    @abstractmethod
    def update_type(self) -> UpdateType:
        ...

    @abstractmethod
    def create_unified_callback(self) -> HandlerSignature:
        ...

    def get_description(self) -> str:
        parts = []
        if self.triggers.action is not None:
            parts += "ActionHandler("

            if self.plan._handler:
                parts += {self.plan._handler.name}
            elif (view := self.plan._view) :

                # TODO: nice string from the view parameters
                parts += view.command.title()
                parts += " "
                parts += (
                    view.view.__class__.__name__
                    if inspect.isclass(view.view)
                    else view.view.__name__
                )
                parts += str(view.send_target)

            if self.plan._reducer:
                reducer_name = self.plan._reducer.name
                if "lambda" not in reducer_name:
                    parts += f", reducer={reducer_name}"

            if self.plan._gatherer:
                gatherer_name = self.plan._gatherer.name
                if "lambda" not in gatherer_name:
                    parts += f", reducer={gatherer_name}"
        else:
            pipeline_name = self.__class__.__name__.replace("Factory", "")

            parts += f"{pipeline_name}("
            if self.plan._handler:
                parts += self.plan._handler.name
            else:
                args = []
                if self.plan._gatherer:
                    args += f"gatherer={self.plan._gatherer}"
                if self.plan._reducer:
                    args += f"reducer={self.plan._reducer}"
                if self.plan._view:
                    args += f"view={self.plan._view.view}"
                parts += ", ".join(args)

        if self.triggers.filters is not None:
            parts += ", filters="
            parts += type(self.triggers.filters).__name__

        parts += ")"
        return "".join(parts)

    def create_update_filter(self) -> UpdateFilterSignature:
        return self.triggers.filters
        cond = self.triggers.condition
        filters = self.triggers.filters

        cond_is_awaitable = cond and inspect.isawaitable(cond)

        async def check(client: IClient, update: Update) -> bool:
            if cond is not None:

                if cond_is_awaitable:
                    if not await cond():
                        return False

            if filters:
                try:
                    return await filters(client, update)
                except:
                    print(filters)
                    print(type(filters))
                    traceback.print_exc()

            return False

        # TODO: Hotfix for weird PR in pyro
        check.__call__ = check

        return check
