from __future__ import annotations
from typing import *
import re

from loguru import logger
from loguru._logger import Logger


# def botkit_log_filter(record):
#     return (
#         "botkit" in record["extra"]
#         and record["level"].no >= logger.level(botkit_settings.log_level).no
#     )


def create_logger(sub_logger_name: Optional[str] = None, **kwargs: Any) -> Logger:
    if sub_logger_name:
        name = "botkit." + re.sub(r"^botkit\.?", "", sub_logger_name, re.MULTILINE)
    else:
        name = "botkit"

    # Then you can use this one to log all messages
    log = logger.bind(identity=name, botkit=True)

    return log
