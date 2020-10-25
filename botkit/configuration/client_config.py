from dataclasses import field
from dataclasses import field
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Type, Union

from boltons.strutils import slugify
from haps import base
from pydantic import DirectoryPath, FilePath, constr, root_validator, validator
from pydantic.dataclasses import dataclass

from botkit.agnostic.library_checks import SupportedLibraryName, ensure_installed


class ClientType(Enum):
    user = "user"
    bot = "bot"


@dataclass
class APIConfig:
    api_id: Union[int, str]
    api_hash: str

    def as_kwargs(self) -> Dict:
        return dict(api_id=self.api_id, api_hash=self.api_hash)


BotToken = constr(strip_whitespace=True, regex=r"[0-9]{8,10}:AA[a-zA-Z0-9-_]{33}")
PhoneNumber = Union[int, constr(regex=r"^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$")]


@base
@dataclass
class ClientConfig:
    client_type: ClientType
    flavor: SupportedLibraryName

    session_root_dir: DirectoryPath = field(default_factory=lambda: Path.cwd().absolute())

    session_string: Optional[constr(strip_whitespace=True, min_length=30)] = None
    session_file: Optional[Union[FilePath, str]] = None

    bot_token: Optional[BotToken] = None
    phone_number: Optional[PhoneNumber] = None

    @validator("flavor")
    def check_library_is_installed(cls, flavor):
        ensure_installed(flavor)
        return flavor

    @root_validator
    def ensure_sufficient_properties_present(cls, values):
        bot_token, phone_number = values.get("bot_token"), values.get("phone_number")

        client_type = values.get("client_type")

        if client_type == ClientType.bot and phone_number:
            raise ValueError("A bot client cannot have a phone number.")

        if client_type == ClientType.user and bot_token:
            raise ValueError("A user client cannot have a bot token.")

        if values.get("session_string") or values.get("session_file"):
            return values

        if client_type == ClientType.bot and not bot_token:
            raise ValueError("A bot client should have a token or re-use an existing session.")
        if client_type == ClientType.user and not phone_number:
            raise ValueError(
                "A user client should have a phone number or re-use an existing session."
            )

    @root_validator(pre=True)
    def make_library_dependent(cls, values):
        session_file = values.get("session_file")

        if not session_file:
            if bot_token := values.get("bot_token"):
                session_file = bot_token.split(":")[0]
            elif phone_number := values.get("phone_number"):
                session_file = slugify(str(phone_number), delim="")

        # if session_file:
        #     # Pyrogram session names need to end in ".session"
        #     if flavor == "pyrogram" and not str(session_file).endswith(".session"):
        #         session_file = f"{session_file}.session"

        values["session_file"] = session_file

        return values

    @property
    def is_local_file_session(self) -> bool:
        return not self.session_string

    @property
    def full_session_path(self) -> Optional[FilePath]:
        if self.session_string or not self.effective_session_location:
            return None
        # noinspection PydanticTypeChecker
        return Path(f"{self.effective_session_location}.session")

    @property
    def description(self) -> str:
        result = f"{self.flavor} {self.client_type.value} client "

        if self.session_string:
            result += "using a string session"
        elif self.session_file:
            result += f"using session file {self.session_file}"
        return result

    @property
    def effective_session_location(self):
        if self.session_string:
            if self.flavor == "telethon":
                # noinspection PyUnresolvedReferences
                from telethon.sessions import StringSession

                return StringSession(self.session_string)
            return self.session_string
        if self.session_file:
            return str(self.session_root_dir / self.session_file)

        raise ValueError("Could not find a valid session")

    # TODO: add validators for item combinations
    # https://pydantic-docs.helpmanual.io/usage/validators/

    def init_kwargs(self, api_config: APIConfig = None) -> Dict:
        result = {}

        if self.bot_token:
            if self.flavor != "telethon":
                result["bot_token"] = self.bot_token

        if self.flavor == "pyrogram":
            if self.is_local_file_session:
                result["session_name"] = self.session_file
                result["workdir"] = self.full_session_path.parent
            else:
                result["session_name"] = self.effective_session_location
        else:
            result["session"] = self.effective_session_location

        if self.flavor == "pyrogram" and self.phone_number:
            result["phone_number"] = str(self.phone_number)
        # Note: Phone number gets passed to Telethon clients in `start`

        if api_config:
            result.update(api_config.as_kwargs())

        return result

    def start_kwargs(self) -> Dict:
        if self.flavor == "pyrogram":
            return {}
        if self.flavor == "telethon":
            if self.phone_number:
                return {"phone": self.phone_number}
            if self.bot_token:
                return {"bot_token": self.bot_token}
            return {}

        raise ValueError("Start args unknown for library")

    # TODO
    # @validator("session_string", "session_path")
    # def check_session_string_or_session_path_present(cls, session_string: Optional[str], session_path: Optional[str]):
    #     if session_string.


class ClientConfigurationError(Exception):
    def __init__(self, passed_config: ClientConfig, client_type: Type):
        self.config = passed_config
        self.client_type = client_type
        super(ClientConfigurationError, self).__init__(self.__str__())

    def __str__(self) -> str:
        # TODO: refactor
        msg = "Configuration failed for "
        msg += self.client_type
        # if hasattr(self.client_type, "__class__"):
        #     msg += self.client_type.__class__.__name__
        # else:
        #     msg += str(self.client_type)

        msg += " using "

        kwargs = self.config.init_kwargs()
        msg += kwargs["session"]

        msg += "."
        return msg
