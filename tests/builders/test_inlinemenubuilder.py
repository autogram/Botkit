from haps import Container, Egg
from pyrogram import InlineKeyboardButton

from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from botkit.dispatching.callbackqueries.callback_manager import ICallbackManager, LocalDictCallbackManager
from botkit.dispatching.callbackqueries.callback_manager._simple import lookup_callback
from botkit.settings import botkit_settings

Container.configure(
    [Egg(ICallbackManager, ICallbackManager, botkit_settings.callback_manager_qualifier, LocalDictCallbackManager)]
)


def test_add_button__is_available():
    builder = InlineMenuBuilder({"my": "choices"})

    builder.rows[0].switch_inline_button("test")

    keyboard = builder.render()

    assert keyboard[0][0].text == "test"
    assert keyboard[0][0].switch_inline_query_current_chat == ""


def test_add_buttons_to_rows__structure_is_correct():
    builder = InlineMenuBuilder({"my": "choices"})

    builder.rows[1].switch_inline_button("row1_col0").switch_inline_button("row1_col1")
    builder.rows[1].switch_inline_button("row1_col2")

    builder.rows[3].switch_inline_button("row3_col0").switch_inline_button("row3_col1")

    keyboard = builder.render()

    assert keyboard[0][0].text == "row1_col0"
    assert keyboard[0][1].text == "row1_col1"
    assert keyboard[0][2].text == "row1_col2"
    assert keyboard[1][0].text == "row3_col0"
    assert keyboard[1][1].text == "row3_col1"


def test_buttons_retain_state_and_payload():
    state = {"my": "choices"}
    builder = InlineMenuBuilder(state)
    b = builder.rows[1].action_button("caption", "test_action", payload="test_payload")

    keyboard = builder.render()
    res: InlineKeyboardButton = keyboard[0][0]

    cb = lookup_callback(res.callback_data)
    assert cb.state == state
    assert cb.payload == "test_payload"
    assert cb.action == "test_action"
