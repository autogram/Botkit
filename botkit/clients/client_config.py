from dataclasses import dataclass
from typing import Optional

from decouple import config


class ClientConfig:
    session_string: Optional[str] = None
    session_path: Optional[str] = None
    bot_token: Optional[str] = None
    phone_number: Optional[str] = None
