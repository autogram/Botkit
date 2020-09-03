import logging
from typing import List


def get_all_botkit_loggers() -> List[logging.Logger]:
    # noinspection PyUnresolvedReferences
    existing_loggers = [
        logging.getLogger(name) for name in logging.root.manager.loggerDict if "botkit." in name
    ]
    existing_loggers.append(logging.getLogger("botkit"))
    return existing_loggers


def set_botkit_log_level(value):
    # This is a hack because for some reason changing the "botkit.*" root logger for existing handlers has no
    # effect. Therefore we set the level for every existing logger individually.
    for logger in get_all_botkit_loggers():
        logger.setLevel(value)
