from typing import Any

from botkit.utils.botkit_logging.setup import create_logger
from botkit.views.botkit_context import Context

log = create_logger("state_generation")


def update_view_state_if_applicable(state_generation_result: Any, context: Context) -> bool:
    if state_generation_result:
        context.view_state = state_generation_result
        return True
    return False
