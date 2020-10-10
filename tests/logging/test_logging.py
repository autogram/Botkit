import logging
from unittest import mock

import pytest
from loguru import logger

from botkit.settings import botkit_settings
from botkit.utils.botkit_logging.setup import create_logger


# region fixtures


@pytest.fixture(autouse=True)
def reset_botkit_logger_before_every_test():
    # TODO
    yield


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)


# endregion

# region tests


def test_botkit_loguru_can_log_when_level_set_before_creation(caplog):
    botkit_settings.log_level = "DEBUG"

    log = create_logger("test_logging")

    with caplog.at_level(logging.DEBUG):
        log.debug("debug")
        assert caplog.record_tuples == [
            ("test_logging", 10, "debug {'name': 'botkit.test_logging'}")
        ]


def test_botkit_loguru_can_log_when_level_set_after_creation(caplog):
    log = create_logger("test_logging")

    botkit_settings.log_level = "DEBUG"
    with caplog.at_level(logging.DEBUG):
        log.debug("debug")
        assert caplog.record_tuples == [
            ("test_logging", 10, "debug {'name': 'botkit.test_logging'}")
        ]


def test_botkit_loguru_sub_logger_can_log_when_level_set_before_creation(caplog):
    botkit_settings.log_level = "DEBUG"

    log = create_logger("test")

    with caplog.at_level(logging.DEBUG):
        log.debug("debug")
        assert caplog.record_tuples == [("test_logging", 10, "debug {'name': 'botkit.test'}")]


def test_botkit_loguru_sub_logger_can_log_when_level_set_after_creation(caplog):
    log = create_logger("test")

    with caplog.at_level(logging.DEBUG):
        botkit_settings.log_level = "DEBUG"
        log.debug("debug")
        assert caplog.record_tuples == [("test_logging", 10, "debug {'name': 'botkit.test'}")]


def test_botkit_loguru_sub_logger_level_can_be_increased_from_root_before_creation(caplog,):
    botkit_settings.log_level = "INFO"
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
    def bind_mock(**kwargs):
        assert "name" in kwargs
        assert kwargs["name"] == exp_name

    with mock.patch.object(logger, "bind", bind_mock):
        create_logger(name)


# endregion
