from typing import Type

import pytest

from botkit.widgets._base import HtmlWidget, MenuWidget, MetaWidget


def pytest_generate_tests(metafunc):
    if "widget_type" in metafunc.fixturenames:
        metafunc.parametrize("widget_type", [HtmlWidget, MenuWidget, MetaWidget])


def test_error_class_missing_abstract_method(widget_type: Type):
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        widget_type()
