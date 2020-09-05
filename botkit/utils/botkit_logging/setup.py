import re
from typing import Any

import logzero

from botkit.settings import botkit_settings
from botkit.utils.botkit_logging.chatlogger import ChatLogHandler


def create_logger(
    sub_logger_name: str = None, override_level: Any = None, use_standard_format: bool = True,
):
    level = override_level or botkit_settings.log_level

    if sub_logger_name:
        name = "botkit." + re.sub(r"^botkit\.?", "", sub_logger_name, re.MULTILINE)
    else:
        name = "botkit"

    if use_standard_format:
        return logzero.setup_logger(
            name=name, formatter=botkit_settings.log_formatter, level=level
        )

    log = logzero.setup_logger(name=name, level=level)

    if botkit_settings.additional_log_handlers:
        for handler in botkit_settings.additional_log_handlers:
            log.addHandler(handler)

    return log
