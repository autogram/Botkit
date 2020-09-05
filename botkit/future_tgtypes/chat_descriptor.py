from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class PeerDescriptor:
    chat_id: Optional[int] = None
    username: Optional[str] = None
    title: Optional[str] = None
