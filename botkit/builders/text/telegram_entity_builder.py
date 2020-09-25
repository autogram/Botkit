from typing import Any, Iterable, Literal, Optional, TYPE_CHECKING, Union
from urllib.parse import quote_plus, urlencode

from boltons import strutils
from haps import Container
from unsync import Unfuture

from botkit.builders.text.htmltextbuilder import _HtmlTextBuilder
from botkit.persistence.callback_store import CallbackActionContext, ICallbackStore
from botkit.routing.triggers import ActionIdType
from botkit.settings import botkit_settings
from botkit.utils.cached_property import cached_property

if TYPE_CHECKING:
    from botkit.types.client import IClient, IdentifiableUser
else:
    IClient = None


class NavigationBuilder(_HtmlTextBuilder):
    @classmethod
    def as_command(cls, name: str, to_lower: bool = False):
        name = name.lstrip("/")
        name = strutils.slugify(str(name), delim="", lower=to_lower, ascii=True).decode("utf-8")
        return f"/{name}"

    def command(self, name: str, to_lower: bool = False, end: Optional[str] = " "):
        return self._append_with_end(self.as_command(name=name, to_lower=to_lower), end)

    @classmethod
    def as_hashtag(cls, name: str):
        name = name.replace(" ", "")
        return f"#{name}"

    def hashtag(self, name: str, end: Optional[str] = " "):
        self._append_with_end(self.as_hashtag(name), end)

    def as_tag_list(self, tag_names: Iterable[str]):
        return " ".join(self.as_hashtag(n) for n in tag_names)

    def tag_list(self, tag_names: Iterable[str], end: Optional[str] = " "):
        return self._append_with_end(self.as_tag_list(tag_names), end)

    def command(self, name: str, to_lower: bool = False, end: Optional[str] = " "):
        return self._append_with_end(self.as_command(name=name, to_lower=to_lower), end)

    @classmethod
    def as_prompt(cls, text: str) -> "str":
        text = quote_plus(text)
        return f"https://telegram.me/share/url?url={text}"

    def deep_link_start(
        self,
        text: str,
        to_bot: Union[IClient, str],
        action: ActionIdType,
        payload: Any = None,
        end: str = None,
        start_type: Literal["start", "startgroup"] = "start",
    ):
        if not isinstance(to_bot, str):
            me: IdentifiableUser = Unfuture(to_bot.get_me()).result()
            to_bot = me.username

        to_bot = to_bot.lstrip("@")

        # TODO: add the other parameters like notification?
        cb = self.callback_builder.create_callback(
            action_id=action, payload=payload, triggered_by="command"
        )

        return self.link(text, f"https://t.me/{to_bot}?{start_type}={cb}", end=end)
