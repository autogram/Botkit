from collections import namedtuple
from typing import Any, Awaitable, Callable, List, Optional, Union

from pyrogram.errors import MessageIdInvalid

from botkit.future_tgtypes.chat_descriptor import ChatDescriptor
from botkit.future_tgtypes.message_descriptor import MessageDescriptor
from botkit.routing.pipelines.execution_plan import SendTarget, SendTo, ViewParameters
from botkit.routing.pipelines.factory_types import IStepFactory
from botkit.routing.pipelines.steps._base import StepError
from botkit.routing.update_types.updatetype import UpdateType
from botkit.services.companionbotservice import CompanionBotService
from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context


class CommitRenderedViewStepError(StepError):
    pass


EvaluatedSendTarget = namedtuple("EvaluatedSendTarget", ["peer_id", "reply_to_msg_id"])


class CommitRenderedViewStepFactory(
    IStepFactory[ViewParameters, Optional[Callable[[Context], Awaitable[Any]]]]
):
    @property
    def applicable_update_types(self) -> List[UpdateType]:
        return [UpdateType.message, UpdateType.callback_query, UpdateType.poll]

    # TODO: something breaks PyCharm's type inference here...
    @classmethod
    def create_step(cls, view_params: ViewParameters):
        if view_params is None:
            return None

        log = create_logger("sender")
        send_target = view_params.send_target

        if view_params.command == "send":

            async def send_view(context: Context) -> None:
                try:
                    client = view_params.send_from if view_params.send_from else context.client
                    target = evaluate_send_target(send_target, context)

                    reply_log = (
                        f" quoting message {target.reply_to_msg_id}"
                        if target.reply_to_msg_id
                        else ""
                    )

                    if view_params.send_via_bot is not None:
                        log.debug(
                            f"Sending rendered message via bot client to {target.peer_id}{reply_log}"
                        )
                        companion = CompanionBotService(client, view_params.send_via_bot)
                        sent = await companion.send_rendered_message_via(
                            target.peer_id,
                            rendered=context.rendered_message,
                            reply_to=target.reply_to_msg_id,
                        )
                        context._data["inline_message_id"] = sent.inline_message_id
                    else:
                        log.debug(f"Sending rendered message to {target}{reply_log}")
                        await client.send_rendered_message(
                            peer=target.peer_id,
                            rendered=context.rendered_message,
                            reply_to=target.reply_to_msg_id,
                        )
                except Exception as e:
                    raise CommitRenderedViewStepError(e)

            return send_view

        elif view_params.command == "update":

            async def update_view(context: Context):
                try:
                    # TODO: Not sure if send_from was indeed meant to be used only for sending
                    client = view_params.send_from if view_params.send_from else context.client

                    if (
                        inline_message_id := getattr(context.update, "inline_message_id", None)
                    ) is not None:
                        try:
                            return await client.update_inline_message_with_rendered(
                                inline_message_id, context.rendered_message
                            )
                        except MessageIdInvalid:
                            # TODO should be fixed, remove as soon as Dan has published
                            # Then replace with proper error handling..?
                            log.exception("Message ID invalid bug encountered.")
                            return None

                    # We need to differentiate button clicks on regular and inline (query) messages:
                    # TODO: Merge all these into Context
                    if (message := getattr(context.update, "message", None)) is not None:
                        # CallbackQuery with message
                        chat_id = message.chat.id
                        message_id = message.message_id
                    elif hasattr(context.update, "message_id"):
                        # Message update
                        chat_id = context.chat.id
                        message_id = context.update.message_id
                    else:
                        chat_id = context.user_id
                        message_id = context.message_id

                    log.debug(f"Updating inline message in chat {chat_id} with rendered content")
                    return await client.update_message_with_rendered(
                        peer=chat_id, message_id=message_id, rendered=context.rendered_message,
                    )
                except Exception as e:
                    raise CommitRenderedViewStepError(e)

            return update_view


def evaluate_send_target(send_target: SendTarget, context: Context) -> EvaluatedSendTarget:
    assert send_target is not None

    def resolve_chat_id(value: Union[int, ChatDescriptor]) -> Union[SendTo, int]:
        # TODO: allow MessageDescriptors, add tests
        if not isinstance(value, ChatDescriptor):
            return value
        return value.get_chat_id(context.client.own_user_id)

    if callable(send_target):
        static_send_target = send_target(context)
        if isinstance(static_send_target, tuple):
            return EvaluatedSendTarget(
                resolve_chat_id(static_send_target[0]), static_send_target[1]
            )
    else:
        static_send_target = send_target

    if static_send_target == SendTo.self or static_send_target == SendTo.self.name:
        return EvaluatedSendTarget("me", None)
    if static_send_target == SendTo.same_chat or static_send_target == SendTo.same_chat.name:
        return EvaluatedSendTarget(context.chat_id, None)
    if (
        static_send_target == SendTo.same_chat_quote
        or static_send_target == SendTo.same_chat_quote.name
    ):
        return EvaluatedSendTarget(context.chat_id, context.message_id)
    if (
        static_send_target == SendTo.same_chat_quote_replied_to
        or static_send_target == SendTo.same_chat_quote_replied_to.name
    ):
        return EvaluatedSendTarget(context.chat_id, context.replied_to_message_id)
    if (
        static_send_target == SendTo.same_chat_quote_original_replied_to
        or static_send_target == SendTo.same_chat_quote_original_replied_to.name
    ):
        raise NotImplementedError(
            "The flag `SendTo.same_chat_quote_original_replied_to` is a little harder to "
            "implement, especially in a library-agnostic way. Please create an issue on GitHub "
            "if you need this!"
        )
    if (
        static_send_target == SendTo.user_in_private
        or static_send_target == SendTo.user_in_private.name
    ):
        return EvaluatedSendTarget(context.user_id, None)
    if isinstance(static_send_target, (int, str)):
        return EvaluatedSendTarget(static_send_target, None)
    if isinstance(static_send_target, ChatDescriptor):
        return EvaluatedSendTarget(resolve_chat_id(static_send_target), None)
