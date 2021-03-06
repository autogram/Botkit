from dataclasses import dataclass
from typing import Any, Collection, Dict, Iterator, List, TYPE_CHECKING, Union
from uuid import uuid4

from botkit.builders.callbackbuilder import CallbackBuilder

if TYPE_CHECKING:
    from botkit.widgets import MenuWidget

from pyrogram.types import InlineKeyboardButton

from botkit.inlinequeries.contexts import DefaultInlineModeContext, IInlineModeContext
from botkit.routing.triggers import ActionIdType
from botkit.uncategorized import buttons
from botkit.utils.sentinel import NotSet, Sentinel

MAX_BUTTONS_PER_ROW = 8


@dataclass
class ButtonRow:
    _array: List[InlineKeyboardButton]
    limit: int = MAX_BUTTONS_PER_ROW

    def add_button(self):
        pass


class MenuButtonMatrix:
    def __init__(self):
        self.current_row: int = 0
        self._rows: List[ButtonRow]


# noinspection PyIncorrectDocstring
class InlineMenuRowBuilder:
    def __init__(
        self,
        parent_collection: "InlineMenuRowsCollection",
        callback_builder: CallbackBuilder,
        *,
        override_buttons: List[Any] = None,
    ):
        self._parent_collection = parent_collection
        if override_buttons:
            self.buttons = override_buttons
        else:
            self.buttons: List[InlineKeyboardButton] = []

        self._callback_builder = callback_builder
        self._limit = MAX_BUTTONS_PER_ROW

    @property
    def is_empty(self):
        return not len(self.buttons)

    @property
    def limit(self) -> int:
        return self._limit

    @limit.setter
    def limit(self, num_columns: int):
        self._limit = num_columns

    def switch_inline_button(
        self,
        caption: str,
        in_context: IInlineModeContext = DefaultInlineModeContext(),
        current_chat: bool = True,
    ) -> "InlineMenuRowBuilder":
        button = buttons.switch_inline_button(caption, in_context, current_chat=current_chat)
        self.buttons.append(button)
        return self

    def btn(
        self, caption: str, payload: Any = None,
    ):
        return self.action_button(caption=caption, action=f"test_{uuid4()}", payload=payload,)

    def action_button(
        self,
        caption: str,
        action: ActionIdType,
        payload: Any = None,
        notification: Union[str, None, Sentinel] = NotSet,
        show_alert: bool = False,
    ) -> "InlineMenuRowBuilder":
        """
        :param notification: Defaulting to the caption text, this is the message to be shown at the top of the user's
        screen on button press. Pass `None` to disable.
        :param show_alert: Whether to show the `notification` as an alert. Only applicable if `notification` is not
        None.
        """
        callback_id = self._callback_builder.create_callback(
            action_id=action,
            triggered_by="button",
            payload=payload,
            notification=caption if notification is NotSet else notification,
            show_alert=show_alert,
        )
        button = InlineKeyboardButton(caption, callback_id)
        self.buttons.append(button)
        return self


class InlineMenuRowsCollection(Collection[InlineMenuRowBuilder]):
    def __init__(
        self, callback_builder: CallbackBuilder, *, override_rows: List[List[Any]] = None,
    ):
        self._callback_builder = callback_builder
        if override_rows:
            self._rows = {
                n: InlineMenuRowBuilder(
                    parent_collection=self,
                    callback_builder=self._callback_builder,
                    override_buttons=x,
                )
                for n, x in enumerate(override_rows)
            }
        else:
            self._rows: Dict[int, InlineMenuRowBuilder] = {}

    def __len__(self) -> int:
        return len(self._get_nonempty_rows())

    def __iter__(self) -> Iterator[InlineMenuRowBuilder]:
        return iter(self._get_nonempty_rows())

    def __contains__(self, __x: Any) -> bool:
        return False  # TODO: implement???

    def __getitem__(self, index: int) -> InlineMenuRowBuilder:
        if index < 0:
            # TODO: apply modulo and document what this does
            index = len(self._rows) - 2 - index
        return self._rows.setdefault(
            index, InlineMenuRowBuilder(self, callback_builder=self._callback_builder)
        )

    def _get_nonempty_rows(self) -> List[InlineMenuRowBuilder]:
        return [x for x in self._rows.values() if not x.is_empty]


class MenuBuilder:
    def __init__(self, callback_builder: CallbackBuilder):
        self._callback_builder = callback_builder
        self._rows = InlineMenuRowsCollection(callback_builder=callback_builder)

        self.force_reply = False

    def add(self, widget: "MenuWidget") -> "MenuBuilder":
        widget.render_menu(self)
        return self

    @property
    def is_dirty(self) -> bool:
        return bool(self._rows._get_nonempty_rows()) or self.force_reply

    def add_rows(self, rows: Collection[InlineKeyboardButton]) -> "MenuBuilder":
        # TODO: should also take a row builder
        pass  # TODO: implement

    def render(self):
        result = [x.buttons for x in self.rows]
        if not result or not result[0]:
            result = None
        return result

    @property
    def rows(self) -> InlineMenuRowsCollection:
        return self._rows

    @rows.setter
    def rows(self, value):
        self._rows = InlineMenuRowsCollection(
            callback_builder=self._callback_builder, override_rows=value
        )
