from typing import Any, Iterable, Literal, Optional, TYPE_CHECKING, Union
from urllib.parse import quote_plus

from boltons import strutils
from pyrogram.emoji import BUST_IN_SILHOUETTE

from botkit.builders.text.htmltextbuilder import _HtmlTextBuilder
from botkit.routing.triggers import ActionIdType
from botkit.tghelpers.direct_links import direct_link, direct_link_user
from botkit.tghelpers.names import display_name

if TYPE_CHECKING:
    from botkit.clients.client import IClient
else:
    IClient = None


class EntityBuilder(_HtmlTextBuilder):
    @classmethod
    def as_user(cls, user: Any):
        link = cls.as_link(display_name(user), direct_link_user(user))
        return f"{BUST_IN_SILHOUETTE} {link}"

    def user(self, user: Any, end: Optional[str] = " "):
        return self._append_with_end(self.as_user(user=user), end)

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

    def as_deep_link_start(
        self,
        text: str,
        to_bot: Union[IClient, str],
        action: ActionIdType,
        payload: Any = None,
        end: str = None,
        start_type: Literal["start", "startgroup"] = "start",
    ):
        if not isinstance(to_bot, str):
            if hasattr(to_bot, "own_username"):
                to_bot = to_bot.own_username
            else:
                raise ValueError(f"Could not determine username for {to_bot}", to_bot)

        to_bot = to_bot.lstrip("@")

        cb = self.callback_builder.create_callback(
            action_id=action, payload=payload, triggered_by="command"
        )

        return self.as_link(text, f"https://t.me/{to_bot}?{start_type}={cb}", end=end)

    def deep_link_start(
        self,
        text: str,
        to_bot: Union[IClient, str],
        action: ActionIdType,
        payload: Any = None,
        end: str = None,
        start_type: Literal["start", "startgroup"] = "start",
    ):
        return self.raw(
            self.as_deep_link_start(
                text=text,
                to_bot=to_bot,
                action=action,
                payload=payload,
                end=end,
                start_type=start_type,
            )
        )
