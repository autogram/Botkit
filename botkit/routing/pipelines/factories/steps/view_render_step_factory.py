import inspect
import warnings
from typing import Any, Awaitable, Callable, Optional, cast

from pyrogram import Update
from pyrogram.errors import MessageIdInvalid

from botkit.routing.pipelines.execution_plan import SendTarget, ViewParameters
from botkit.routing.pipelines.factories.factory_types import IStepFactory
from botkit.services.companionbotservice import CompanionBotService
from botkit.views.base import RenderedMessageBase
from botkit.views.botkit_context import BotkitContext
from botkit.views.functional_views import quacks_like_view_render_func, render_functional_view
from botkit.views.views import MessageViewBase


class ViewRenderStepFactory(
    IStepFactory[ViewParameters, Optional[Callable[[BotkitContext], Awaitable[Any]]]]
):
    # TODO: something breaks PyCharm's type inference here...
    @classmethod
    def create_step(cls, view_params: ViewParameters):
        if view_params is None:
            return None

        is_view_render_func = quacks_like_view_render_func(view_params.view)
        create_view_instance_dynamically = inspect.isclass(view_params.view)

        def render_view(context: BotkitContext) -> RenderedMessageBase:
            if is_view_render_func:
                return render_functional_view(view_params.view, context.state)

            elif create_view_instance_dynamically:
                view_instance = view_params.view(context.state)

                if context.state is None:
                    # First try to instantiate the view, then warn if that succeeded without an exception despite
                    # a `None`-state.
                    warnings.warn(
                        f"`None` state is being passed to view {view_params.view}. Check your state generation "
                        f"and/or mutations."
                    )

                return view_instance.render()

            else:
                return cast(MessageViewBase, view_params.view).render()

        if view_params.command == "send":

            async def send_view(context: BotkitContext) -> None:
                chat_id = context.chat.id  # TODO: take target from view_params

                rendered = render_view(context)

                if view_params.send_via is not None:
                    companion = CompanionBotService(context.client, view_params.send_via)
                    await companion.send_rendered_message(chat_id, rendered=rendered)
                else:
                    await context.client.send_rendered_message(peer=chat_id, rendered=rendered)

            return send_view

        elif view_params.command == "update":

            async def update_view(context: BotkitContext):
                rendered = render_view(context)

                if (
                    inline_message_id := getattr(context.update, "inline_message_id", None)
                ) is not None:
                    try:
                        return await context.client.update_inline_message_with_rendered(
                            inline_message_id, rendered
                        )
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

                return await context.client.update_message_with_rendered(
                    peer=chat_id, message_id=message_id, rendered=rendered
                )

            return update_view


def get_send_target(update: Update, send_target: SendTarget):
    pass  # TODO
