from abc import abstractmethod
from typing import Any, Callable, Generic, List, Optional, TypeVar

from haps import base
from pydantic.dataclasses import dataclass

T = TypeVar("T")


@dataclass
class _OptionBase(Generic[T]):
    name: str
    description: str
    default_value: Any


@dataclass
class _OptionDefaults:
    is_global: bool = True
    aliases: Optional[List[str]] = None


@dataclass
class Option(_OptionDefaults, _OptionBase):
    @property
    def all_identifiers(self) -> List[str]:
        return self.aliases + [self.name]


# TODO: should probably not use dataclasses for this...


@dataclass
class _ToggleOptionBase(_OptionBase):
    on_by_default: bool


@dataclass
class _ToggleOptionDefaults:
    on_value: Any = True
    off_value: Any = False
    null_value: Any = None


@dataclass
class ToggleOption(_ToggleOptionDefaults, _OptionDefaults, _ToggleOptionBase):
    @classmethod
    def is_valid(cls, value: Any) -> bool:
        return value in (cls.on_value, cls.off_value)


@dataclass
class _ChoiceOptionBase(_OptionBase):
    choices: List[T]


@dataclass
class ChoiceOption(_OptionDefaults, _ChoiceOptionBase):
    pass


# enabled_modules: ToggleOption[List[str]] = ToggleOption(
#     name="Enabled Modules", description="All modules added to the system on startup.", on_by_default=
# )


class InvalidOptionError(Exception):
    pass


@dataclass
class _ChangeSubscription:
    callback: Callable[[Option, Any], None]
    option: Option
    on_startup: bool


@base
class IOptionStore:
    @abstractmethod
    def add_option(self, option: Option):
        pass

    @abstractmethod
    def remove_option(self, option: Option):
        pass

    @abstractmethod
    def set_value(self, option: Option or str, value: Any, chat: int = None) -> None:
        pass

    @abstractmethod
    def get_global_value(self, option: Option) -> Any:
        pass

    @abstractmethod
    def get_value(self, option: Option or str, chat_id: int) -> Any:
        pass

    @property
    @abstractmethod
    def all_options(self) -> List[Option]:
        pass

    @abstractmethod
    async def on_startup(self) -> None:
        pass

    @abstractmethod
    def subscribe_to_updates(
        self, callback: Callable[[Option, Any], None], for_option: Option, on_startup: bool = False,
    ) -> None:
        pass


# TOGGLES = {
#     'markdown': {
#         'aliases': ['md'],
#         'values': {
#             True: '📝 Better markdown ✅ enabled.',
#             False: '📝 Better markdown 🚫 disabled.',
#         },
#         'per_chat': False,
#         'default': True
#     },
#     'recognition_language': {
#         'aliases': ['rec'],
#         'values': {
#             'de_DE': 'Erkenne Memos in 🇩🇪 Deutsch in diesem Chat.',
#             'en_US': 'Recognition language set to 🇺🇸 English in this chat.'
#         },
#         'per_chat': True,
#         'default': 'en_US'
#     },
#     'auto_responses': {
#         'aliases': ['auto'],
#         'values': {
#             True: 'Auto-responses enabled in this chat.',
#             False: 'Auto-responses stopped in this chat.'
#         },
#         'per_chat': True,
#         'default': False
#     },
#     'spam_responses': {
#         'aliases': ['spam'],
#         'values': {
#             True: 'Spam enabled in this chat.',
#             False: 'Spam stopped in this chat.'
#         },
#         'per_chat': True,
#         'default': False
#     },
#     'sed_replace': {
#         'aliases': ['sed'],
#         'values': {
#             True: 'Sed replacements enabled.',
#             False: 'Sed replacements disabled.'
#         },
#         'per_chat': True,
#         'default': True
#     },
#     'ph_mode': {
#         'aliases': ['ph'],
#         'values': {
#             True: 'sender/ph mode enabled.',
#             False: 'sender/ph mode disabled.'
#         },
#         'per_chat': True,
#         'default': False
#     },
#
