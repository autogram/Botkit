import inspect
import warnings
from typing import Any, Awaitable, Callable, Optional

from pyrogram import Update
from pyrogram.errors import MessageIdInvalid

from botkit.routing.pipelines.execution_plan import SendTarget, ViewParameters
from botkit.routing.pipelines.factory_types import IStepFactory
from botkit.views.botkit_context import BotkitContext
from botkit.views.views import MessageViewBase


class ViewRenderStepFactory(IStepFactory[ViewParameters, Optional[Callable[[BotkitContext], Awaitable[Any]]]]):
    # TODO: something breaks PyCharm's type inference here...
    @classmethod
    def create_step(cls, view_params: ViewParameters):
        if view_params is None:
            return None

        if view_params.command == "send":

            create_view_dynamically = inspect.isclass(view_params.view)

            async def send_view(context: BotkitContext) -> None:
                chat_id = context.chat.id  # TODO: take target from view_params

                if create_view_dynamically:
                    view_instance = view_params.view(context.state)

                    # First try to instantiate the view, then warn if that succeeded without an exception.
                    if context.state is None:
                        warnings.warn(
                            f"None state is being passed to view {view_params.view}. Check your state generation "
                            f"and/or mutations."
                        )

                else:
                    view_instance = view_params.view

                await context.client.send_view(peer=chat_id, view=view_instance)

            return send_view

        elif view_params.command == "update":

            async def update_view(context: BotkitContext):
                # Instantiate the view with state as argument
                view: MessageViewBase = view_params.view(context.state)

                # First try to instantiate the view, then warn if that succeeded without an exception.
                if context.state is None:
                    warnings.warn(
                        f"None state is being passed to view {view_params.view}. Check your state generation "
                        f"and/or mutations."
                    )

                if (inline_message_id := getattr(context.update, "inline_message_id", None)) is not None:
                    try:
                        return await context.client.update_inline_view(inline_message_id, view)
                    except MessageIdInvalid:
                        # TODO should be fixed, remove as soon as Dan has published
                        # Then replace with proper error handling..?
                        print("Message ID invalid bug encountered.")
                        return None

                # We need to differentiate button clicks on regular and inline (query) messages:
                # TODO: Merge all these into BotkitContext
                if (message := getattr(context.update, "message", None)) is not None:
                    # CallbackQuery with message
                    chat_id = message.chat.id
                    message_id = message.message_id
                elif hasattr(context.update, "message_id"):
                    # Message update
                    chat_id = context.chat.id
                    message_id = context.update.message_id
                else:
                    chat_id = context.update.from_user.id
                    message_id = context.update.id

                return await context.client.update_view(peer=chat_id, message=message_id, view=view)

            return update_view


def get_send_target(update: Update, send_target: SendTarget):
    pass  # TODO
