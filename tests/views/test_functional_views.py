from dataclasses import dataclass

from botkit.builders import ViewBuilder
from botkit.persistence import callback_manager
from botkit.views.functional_views import render_functional_view, view


@dataclass
class TestModel:
    pass


DESCRIPTION = "Henlo fren!"
TITLE = "Saying henlo!"


@view
def full_view_experiment(state: TestModel, builder: ViewBuilder):
    builder.html.text("Henlo my").spc
    builder.html.bold("bestest", end=" ").mono("fren")

    builder.menu.rows[0].action_button("row 0, col 0", action="test")
    builder.menu.rows[0].action_button("row 0, col 1", action="test")
    builder.menu.rows[1].action_button("row 1, col 0", action="test")

    builder.meta.description = DESCRIPTION
    builder.meta.title = TITLE


def test_full_view_can_be_rendered(di):
    di(callback_manager)
    res = render_functional_view(full_view_experiment, TestModel())
    assert res.text == "Henlo my <b>bestest</b> <code>fren</code>"
    assert len(res.inline_keyboard_markup.inline_keyboard) == 2
    assert res.description == DESCRIPTION
    assert res.title == TITLE


# def test_using_photo_rendered_message_is_media():
#     def f(_, builder: ViewBuilder):
#         builder.
#
#     render_functional_view()
