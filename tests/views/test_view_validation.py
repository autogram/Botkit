# import inspect
# from typing import Any
# from unittest.mock import MagicMock
#
# from boltons.iterutils import flatten
#
# from botkit.builders import ViewBuilder
# from botkit.persistence import callback_store
# from botkit.views.functional_views import render_functional_view
#
#
# def render_shit(state: Any, builder: ViewBuilder) -> None:
#     builder.html.text("Henlo frens!")
#
#     for x in state:
#         builder.menu.rows[0].action_button(x.name, "some_action", payload="testing")
#
#
# def test_experiment(di):
#     di(callback_store)
#     print(inspect.getsource(render_shit))
#     mocked_state = MagicMock()
#     mocked_state.__iter__.return_value = [mocked_state, mocked_state]
#     rendered = render_functional_view(render_shit, mocked_state)
#
#     assert bool(rendered.inline_keyboard_markup.inline_keyboard)
