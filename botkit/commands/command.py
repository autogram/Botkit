from dataclasses import dataclass, field

from mypy_extensions import TypedDict
from pyrogram import Update
from pyrogram.client.filters.filter import Filter
from typing import Union, Dict, List, Tuple, Optional
from typing_extensions import Literal
import pyrogram

from botkit.utils.dataclass_helpers import default_field

default_prefixes: List[str] = ["/", "#", "."]

CommandCategory = TypedDict("CommandCategory", {"privacy": Literal["self", "public"]})

command_categories: Dict[str, CommandCategory] = {
    "user": {"privacy": "self"},
    "bot": {"privacy": "public"},
}





# trigger_dict = {"private": True, "contains_url": True}
#
# trigger_text = "private & containsUrl"
#
# command_definition_yaml_example = """
# browse:
#   quick_action_filter:
#     - private
#     - contains_url
#   quick_action_prompt: yes
# """


# CommandDefinition(
#     name="browse",
#     quick_action=QuickAction(
#         trigger=EntityFilters.url & Filters.private,
#     ),
#     quick_action_prompt=True,  # actions get included in quick actions reply keyboard
#     delete_query=True
# )


@dataclass
class CommandParser:
    name: str
    aliases: List[str] = field(default_factory=list)
    prefixes: List[str] = default_field(default_prefixes)

    @classmethod
    def from_declaration(
            cls, value: Union[str, List[str], Tuple[str], "CommandParser"]
    ) -> "CommandParser":
        if isinstance(value, CommandParser):
            return value  # for when user already provides initialized object
        if isinstance(value, (tuple, list)):
            return CommandParser(name=value[0], aliases=list(value[1:]))
        else:
            return CommandParser(name=value)


@dataclass
class QuickAction:
    trigger: Filter
    prominence: int = 0  # or "priority", or "importance"..?


@dataclass
class CommandDefinition:
    name: str
    parser: CommandParser

    quick_action: Optional[QuickAction] = None

    delete_query: bool = False
    quote: bool = True
    reply_to_replied: bool = False


# region Routing

QUICK_ACTION_UPDATE_TYPES = (pyrogram.Message, pyrogram.Poll)


async def match_quick_actions(commands: List[CommandDefinition], update: Update):
    if not isinstance(update, QUICK_ACTION_UPDATE_TYPES):
        return



# endregion
