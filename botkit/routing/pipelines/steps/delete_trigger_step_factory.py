from typing import Awaitable, Callable, List, Optional

from botkit.routing.pipelines.factory_types import IStepFactory
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context


class DeleteTriggerStepFactory(IStepFactory[bool, Optional[Callable[[Context], Awaitable[None]]]]):
    @property
    def applicable_update_types(self) -> List[UpdateType]:
        return [UpdateType.message]

    @classmethod
    def create_step(cls, user_input):
        if user_input is False:
            return None

        log = create_logger("delete_trigger")

        async def delete_trigger_message(context: Context) -> None:
            if hasattr(context.update, "delete"):
                await context.update.delete()
            elif hasattr(context.client, "delete_message"):
                raise NotImplementedError(
                    "The delete_message function has not been implemented for trigger removals."
                )
            elif hasattr(context.client, "delete_messages"):
                raise NotImplementedError(
                    "The delete_messages function has not been implemented for trigger removals."
                )
            else:
                log.warning(
                    "It was not possible to delete a trigger message, as neither the update nor the client had any "
                    "delete methods."
                )

        return delete_trigger_message
