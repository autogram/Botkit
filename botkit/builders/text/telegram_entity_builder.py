from typing import Any, Literal, Optional, TYPE_CHECKING, Union
from urllib.parse import urlencode

from boltons import strutils
from haps import Container
from unsync import Unfuture

from botkit.builders.text.basetextbuilder import BaseTextBuilder
from botkit.builders.text.htmltextbuilder import _HtmlTextBuilder

from botkit.persistence.callback_manager import CallbackActionContext, ICallbackManager
from botkit.routing.triggers import ActionIdTypes
from botkit.settings import botkit_settings
from botkit.utils.cached_property import cached_property

if TYPE_CHECKING:
    from botkit.types.client import IClient, IdentifiableUser
else:
    IClient = None


class TelegramEntityBuilder(_HtmlTextBuilder):
    @cached_property
    def _callback_manager(self) -> ICallbackManager:
        return Container().get_object(ICallbackManager, botkit_settings.callback_manager_qualifier)

    @classmethod
    def as_command(cls, name: str, to_lower: bool = False):
        name = name.lstrip("/")
        name = strutils.slugify(str(name), delim="", lower=to_lower, ascii=True).decode("utf-8")
        return f"/{name}"

    def command(self, name: str, to_lower: bool = False, end: Optional[str] = " "):
        return self._append_with_end(self.as_command(name=name, to_lower=to_lower), end)

    @classmethod
    def as_prompt(cls, text) -> "str":
        text = urlencode(text)
        return f"https://telegram.me/share/url?url={text}"

    def deep_link_start(
        self,
        text: str,
        to_bot: Union[IClient, str],
        action: ActionIdTypes,
        payload: Any = None,
        end: str = None,
        start_type: Literal["start", "startgroup"] = "start",
    ):
        if not isinstance(to_bot, str):
            me: IdentifiableUser = Unfuture(to_bot.get_me()).result()
            to_bot = me.username

        to_bot = to_bot.lstrip("@")

        # TODO: add the other parameters like notification?
        cb = self._callback_manager.create_callback(
            CallbackActionContext(
                action=action, state=self.state, payload=payload, triggered_by="command"
            )
        )

        return self.link(text, f"https://t.me/{to_bot}?{start_type}={cb}", end=end)
