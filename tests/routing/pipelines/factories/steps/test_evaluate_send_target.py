from unittest.mock import Mock

import pytest
from pyrogram.types import Chat, Message, User

from botkit.clients.client import IClient
from botkit.routing.pipelines.executionplan import SendTo
from botkit.routing.pipelines.steps.commit_rendered_view_step_factory import evaluate_send_target
from tgtypes.updatetype import UpdateType
from botkit.botkit_context import Context
from tgtypes.identities.chat_identity import ChatIdentity

SAME_CHAT_ID = 123
USER_ID = 321
MESSAGE_ID = 1000
REPLIED_TO_MESSAGE_ID = 2000


@pytest.fixture(scope="function")
def context():
    (replied_to_message := Mock(Message)).configure_mock(message_id=REPLIED_TO_MESSAGE_ID)
    (chat := Mock(Chat)).configure_mock(id=SAME_CHAT_ID)
    (user := Mock(User)).configure_mock(id=USER_ID)
    (message := Mock(Message)).configure_mock(
        chat=chat, message_id=MESSAGE_ID, reply_to_message=replied_to_message, from_user=user,
    )
    (client := Mock(IClient)).configure_mock(own_user_id=0)

    # TODO: Test this with other update types too
    return Context(view_state=None, client=client, update=message, update_type=UpdateType.message)


@pytest.mark.parametrize(
    "send_target,expected",
    [
        (SendTo.self, ("me", None)),
        (SendTo.same_chat, (SAME_CHAT_ID, None)),
        (SendTo.same_chat_quote, (SAME_CHAT_ID, MESSAGE_ID)),
        (SendTo.same_chat_quote_replied_to, (SAME_CHAT_ID, REPLIED_TO_MESSAGE_ID)),
        (SendTo.user_in_private, (USER_ID, None)),
        ("same_chat", (SAME_CHAT_ID, None)),
        ("same_chat_quote", (SAME_CHAT_ID, MESSAGE_ID)),
        ("same_chat_quote_replied_to", (SAME_CHAT_ID, REPLIED_TO_MESSAGE_ID)),
        ("user_in_private", (USER_ID, None)),
        ("@josxa", ("@josxa", None)),
        (12345, (12345, None)),
        (lambda ctx: SendTo.same_chat, (SAME_CHAT_ID, None)),
        (lambda ctx: SendTo.same_chat_quote, (SAME_CHAT_ID, MESSAGE_ID)),
        (lambda ctx: SendTo.same_chat_quote_replied_to, (SAME_CHAT_ID, REPLIED_TO_MESSAGE_ID),),
        (lambda ctx: SendTo.user_in_private, (USER_ID, None)),
        (lambda ctx: "same_chat", (SAME_CHAT_ID, None)),
        (lambda ctx: "same_chat_quote", (SAME_CHAT_ID, MESSAGE_ID)),
        (lambda ctx: "same_chat_quote_replied_to", (SAME_CHAT_ID, REPLIED_TO_MESSAGE_ID),),
        (lambda ctx: "user_in_private", (USER_ID, None)),
        (lambda ctx: "@josxa", ("@josxa", None)),
        (lambda ctx: ("@josxa", 1000), ("@josxa", 1000)),
        (lambda ctx: (12345, 1000), (12345, 1000)),
        (lambda ctx: ("@josxa", None), ("@josxa", None)),
        (lambda ctx: (-100, None), (-100, None)),
        (lambda ctx: ChatIdentity(type="private", peers=1234), (1234, None)),
        (lambda ctx: (ChatIdentity(type="private", peers=1234), 1000), (1234, 1000)),
    ],
)
def test_evaluate_send_target(send_target, expected, context):
    actual = evaluate_send_target(send_target, context)
    res = tuple((actual.peer_id, actual.reply_to_msg_id))
    assert res == expected, f"{res} does not equal {expected}."


SendTargetFuncSignatureExamplesStr = """
def _(ctx: Context) -> SendTo: ...
def _(ctx: Context) -> Union[int, str]: ...
def _(ctx: Context) -> Tuple[SendTo, None]: ...
def _(ctx: Context) -> Tuple[SendTo, int]: ...
"""
