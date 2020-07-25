from dataclasses import dataclass
from typing import Optional

from decouple import config


class ClientConfig:
    session_name: Optional[str] = None
    bot_token: Optional[str] = None
    phone_number: Optional[str] = None
