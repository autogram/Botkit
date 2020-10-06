from typing import *


def display_name(entity: Any) -> str:
    if title := getattr(entity, "title", None):
        return title
    elif first_name := getattr(entity, "first_name", None):
        if last_name := getattr(entity, "last_name", None):
            return f"{first_name} {last_name}"
        return entity.first_name
    raise ValueError(f"The entity of type {type(entity)} does not seem to have a display name.")


def user_or_display_name(entity: Any) -> str:
    if entity.username:
        return f"@{entity.username}"
    return display_name(entity)
