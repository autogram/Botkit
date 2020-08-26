from typing import *


def display_name(entity: Any) -> str:
    if hasattr(entity, "title"):
        return entity.title
    elif hasattr(entity, "first_name"):
        if entity.last_name:
            return f"{entity.first_name} {entity.last_name}"
        return entity.first_name
    raise ValueError("This entity does not seem to have a display name.")


def user_or_display_name(entity: Any) -> str:
    if entity.username:
        return f"@{entity.username}"
    return display_name(entity)
