from datetime import datetime
from typing import Dict

from dataclasses import dataclass


@dataclass
class MessageUnderstanding:
    """
    Dataclass for an incoming utterance, enriched with NLU information.
    """

    text: str
    language_code: str
    intent: str
    action: str
    parameters: Dict[str, str] = None
    contexts: Dict[str, str] = None
    date: datetime = None
    confidence: float = None
