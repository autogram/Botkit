from dataclasses import dataclass

from commons.coreservices.botautomation.base import BotAutomationBase
from haps import base, egg
from typing import Any, List


@dataclass
class CustomReactionsPostRequest:
    to_chat: Any
    media: Any
    emojis: List[str] = None
    caption: str = None
    silent: bool = True


@base
class ToolkitBot(BotAutomationBase):
    username = "@toolkitbot"

    @dataclass
    class State(object):
        pass

    state: State = State()

    # region Public methods

    async def post_media_with_custom_reactions(
        self, request: CustomReactionsPostRequest
    ):
        print("type of photo is:", type(request.media))
        await self.client.send_file(self.username, file=request.media)

        if request.emojis:
            await self.send_message(request.emojis)
        else:
            await self.send_message("No Emojis!")

        print(self.msg.stringify())

        raise NotImplemented  # TODO

    # endregion


@egg
def _factory() -> ToolkitBot:
    return ToolkitBot()
