from typing import Awaitable, Callable, Optional

from botkit.core.components import Component
from botkit.routing.pipelines.factory_types import IStepFactory
from botkit.routing.pipelines.steps._base import StepError
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context


class InvokeComponentStepError(StepError):
    pass


class InvokeComponentStepFactory(
    IStepFactory[Component, Optional[Callable[[Context], Awaitable[None]]]]
):
    @classmethod
    def create_step(cls, component: Component):
        if component is None:
            return None

        log = create_logger("invoker")

        async def invoke_component(context: Context) -> None:
            try:
                log.debug(f"Invoking component {component}")
                await component.invoke(context)
            except Exception as e:
                raise InvokeComponentStepError(e)

        return invoke_component
