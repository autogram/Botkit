import logging
import re
from typing import Any

import logzero

from botkit.settings import botkit_settings

# Ensure botkit's log namespace exists
botkit_logger = logzero.setup_logger(
    name="botkit", formatter=botkit_settings.log_formatter, level=botkit_settings.log_level
)


def create_logger(
    sub_logger_name: str = None, level: Any = logging.NOTSET, use_standard_format: bool = True,
):
    # level = level or botkit_settings.log_level

    if sub_logger_name:
        name = "botkit." + re.sub(r"^botkit\.?", "", sub_logger_name, re.MULTILINE)
    else:
        name = "botkit"

    if use_standard_format:
        return logzero.setup_logger(
            name=name, formatter=botkit_settings.log_formatter, level=level
        )

    log = logzero.setup_logger(name=name, level=level)
    log.propagate = True

    # if botkit_settings.additional_log_handlers:
    #     for handler in botkit_settings.additional_log_handlers:
    #         log.addHandler(handler)

    return log
