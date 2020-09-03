import logging

import pytest

from botkit.settings import botkit_settings
from botkit.utils.botkit_logging.setup import create_logger, get_all_botkit_loggers


@pytest.fixture(autouse=True)
def reset_botkit_logger_before_every_test():
    botkit_settings.log_level = None  # This will reset it to default
    existing_loggers = get_all_botkit_loggers()

    for logger in existing_loggers:
        for h in logger.handlers:
            logger.removeHandler(h)
        for f in logger.filters:
            # Not actually used, but just to be on the safe side...
            logger.removeFilter(f)

    yield


def test_botkit_default_log_level_is_info(caplog):
    log = create_logger()
    assert log.level == logging.INFO


def test_botkit_logzero_can_log_when_level_set_before_creation(caplog):
    botkit_settings.log_level = logging.DEBUG

    log = create_logger()
    log.addHandler(caplog.handler)

    with caplog.at_level(logging.DEBUG):
        log.debug("debug")
        assert caplog.record_tuples == [("botkit", 10, "debug")]


def test_botkit_logzero_can_log_when_level_set_after_creation(caplog):
    log = create_logger()
    log.addHandler(caplog.handler)

    botkit_settings.log_level = logging.DEBUG
    with caplog.at_level(logging.DEBUG):
        log.debug("debug")
        assert caplog.record_tuples == [("botkit", 10, "debug")]


def test_botkit_logzero_sub_logger_can_log_when_level_set_before_creation(caplog):
    botkit_settings.log_level = logging.DEBUG

    log = create_logger("test")
    log.addHandler(caplog.handler)

    with caplog.at_level(logging.DEBUG):
        log.debug("debug")
        assert caplog.record_tuples == [("botkit.test", 10, "debug")]


def test_botkit_logzero_sub_logger_can_log_when_level_set_after_creation(caplog):
    log = create_logger("test")
    log.addHandler(caplog.handler)

    with caplog.at_level(logging.DEBUG):
        botkit_settings.log_level = logging.DEBUG
        log.debug("debug")
        assert caplog.record_tuples == [("botkit.test", 10, "debug")]


def test_botkit_logzero_sub_logger_logs_in_debug(caplog):
    botkit_settings.log_level = logging.DEBUG
    with caplog.at_level(logging.DEBUG):
        sub_log = create_logger("sub")
        sub_log.debug("debug")
        assert caplog.record_tuples == []


def test_botkit_logzero_sub_logger_level_can_be_increased_from_root_before_creation(caplog):
    botkit_settings.log_level = logging.INFO
    with caplog.at_level(logging.INFO):
        sub_log = create_logger("sub")
        sub_log.debug("debug")
        assert caplog.record_tuples == []


@pytest.mark.parametrize(
    "name,exp_name",
    [
        (None, "botkit"),
        ("", "botkit"),
        ("abc", "botkit.abc"),
        ("botkit.abc", "botkit.abc"),
        ("abc_def", "botkit.abc_def"),
        ("abc.def.ghi", "botkit.abc.def.ghi"),
    ],
)
def test_create_logger_name(name, exp_name):
    logger = create_logger(name)
    assert logger.name == exp_name
