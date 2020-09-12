from typing import Any, Collection, Dict, Iterator, List, Optional, Union

from cached_property import cached_property
from haps import Container
from pyrogram.types import InlineKeyboardButton

from botkit.uncategorized import buttons
from botkit.persistence.callback_manager import (
    CallbackActionContext,
    ICallbackManager,
)
from botkit.inlinequeries.contexts import DefaultInlineModeContext, IInlineModeContext
from botkit.settings import botkit_settings
from botkit.utils.sentinel import NotSet, Sentinel


# noinspection PyIncorrectDocstring
class InlineMenuRowBuilder:
    def __init__(self, state: Optional[Any], override_buttons: List[Any] = None):
        if override_buttons:
            self.buttons = override_buttons
        else:
            self.buttons: List[InlineKeyboardButton] = []

        self.state = state

    @cached_property
    def callback_manager(self) -> ICallbackManager:
        # TODO: measure how long this property access takes
        return Container().get_object(ICallbackManager, botkit_settings.callback_manager_qualifier)

    @property
    def is_empty(self):
        return not len(self.buttons)

    def switch_inline_button(
        self,
        caption: str,
        in_context: IInlineModeContext = DefaultInlineModeContext(),
        current_chat: bool = True,
    ) -> "InlineMenuRowBuilder":
        button = buttons.switch_inline_button(caption, in_context, current_chat=current_chat)
        self.buttons.append(button)
        return self

    def action_button(
        self,
        caption: str,
        action: Any,
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
        button = InlineKeyboardButton(
            caption,
            self.callback_manager.create_callback(
                CallbackActionContext(
                    action=action,
                    state=self.state,
                    payload=payload,
                    notification=caption if notification is NotSet else notification,
                    show_alert=show_alert,
                )
            ),
        )
        self.buttons.append(button)
        return self

    # def mutate_button_test(  # TODO
    #     self,
    #     caption: str,
    #     on_click: ReducerSignature,
    #     notification: Union[str, None, Sentinel] = NotSet,
    #     show_alert: bool = False,
    # ) -> "_InlineMenuRowBuilder":
    #     """
    #     :param notification: Defaulting to the caption text, this is the message to be shown at the top of the user's
    #     screen on button press. Pass `None` to disable.
    #     :param show_alert: Whether to show the `notification` as an alert. Only applicable if `notification` is not
    #     None.
    #     """
    #     raise NotImplementedError()


class InlineMenuRowsCollection(Collection[InlineMenuRowBuilder]):
    def __init__(self, state: Optional[Any], override_rows: List[List[Any]] = None):
        self._state = state
        if override_rows:
            self._rows = {
                n: InlineMenuRowBuilder(state=self._state, override_buttons=x)
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
        else:
            index = index
        return self._rows.setdefault(index, InlineMenuRowBuilder(state=self._state))

    def _get_nonempty_rows(self) -> List[InlineMenuRowBuilder]:
        return [x for x in self._rows.values() if not x.is_empty]


class InlineMenuBuilder:
    def __init__(self, state: Optional[Any]):
        self._state = state
        self._rows = InlineMenuRowsCollection(state=self._state)

        self.force_reply = False

    @property
    def is_dirty(self) -> bool:
        return bool(self._rows._get_nonempty_rows()) or self.force_reply

    def add_rows(self, rows: Collection[InlineKeyboardButton]) -> "InlineMenuBuilder":
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
        self._rows = InlineMenuRowsCollection(state=self._state, override_rows=value)
