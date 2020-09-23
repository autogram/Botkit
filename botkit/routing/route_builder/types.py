from typing import Type, TypeVar, Union

from botkit.views.base import InlineResultViewBase
from botkit.views.views import MessageViewBase

V = TypeVar("V", bound=InlineResultViewBase, covariant=True)

TView = Union[V, Type[MessageViewBase]]
