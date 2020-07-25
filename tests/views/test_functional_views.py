from dataclasses import dataclass

from botkit.builders.htmlbuilder import HtmlBuilder
from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from botkit.builders.metabuilder import MetaBuilder
from botkit.views.functional_views import render_functional_view


@dataclass
class TestModel:
    pass


def view(state: TestModel, builder: HtmlBuilder, menu: InlineMenuBuilder, meta: MetaBuilder):
    builder.bold("Helloo")
    menu.rows[0].action_button("test", "test")
    meta.description = "Henlo fren!"


def test_functional_view_can_be_rendered():
    res = render_functional_view(view, TestModel())
