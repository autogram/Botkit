from typing import Optional
import difflib


def string_similarity(user_input: str, compare_to: str) -> float:
    compare_to = compare_to.lower()
    user_input = user_input.lower()

    add = 0
    if user_input in compare_to or compare_to in user_input:
        add = 0.15

    return min(1.0, difflib.SequenceMatcher(None, user_input, compare_to).ratio() + add)


def is_none_or_whitespace(text: Optional[str]) -> bool:
    return text is None or text.strip() == ""


def is_none_or_empty(text: Optional[str]) -> bool:
    return text is None or text == ""
