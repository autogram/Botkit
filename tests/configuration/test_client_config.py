import asyncio
import sys
from unittest.mock import MagicMock, Mock

from decouple import config
from pathlib import Path
from typing import Any, Dict, Optional
from unittest import mock

import pyrogram
import pytest
import telethon
from boltons.iterutils import flatten
from pydantic import ValidationError
from pyrogram import Client as PyrogramClient
from telethon.client import TelegramClient as TelethonClient
from telethon.network import MTProtoSender
from telethon.sessions import StringSession

from botkit.configuration import *
from botkit.configuration.client_config import APIConfig
from botkit.libraries._checks import SupportedLibraries
from tests.configuration.client_config_test_data import (
    TOKEN,
    all_libs_test_configs,
    pyrogram_start_tests,
    telethon_start_tests,
    test_configs,
)


@pytest.fixture(scope="function")
def api_config():
    return APIConfig(api_id=config("API_ID"), api_hash=config("API_HASH"))


def test_simple_instantiation():
    ClientConfig(
        client_type=ClientType.bot, flavor="pyrogram", bot_token=TOKEN,
    )


@pytest.mark.parametrize(
    "ctyp,flavor,expected_error",
    [
        (ClientType.bot, "pyrogram", "should have a token"),
        (ClientType.user, "pyrogram", "should have a phone number"),
        (ClientType.bot, "telethon", "should have a token"),
        (ClientType.user, "telethon", "should have a phone number"),
    ],
)
def test_no_usable_property_validation_error(ctyp, flavor: SupportedLibraries, expected_error):
    with pytest.raises(ValidationError, match=expected_error):
        ClientConfig(client_type=ctyp, flavor=flavor)


@pytest.mark.parametrize(
    "client_type,flavor,session_string,sess_file,token,phone,expected_init_kwargs,expected_start_kwargs,"
    "expected_error",
    all_libs_test_configs,
)
def test_config_path(
    client_type: ClientType,
    flavor: SupportedLibraries,
    session_string: Optional[str],
    sess_file: Optional[str],
    token: Optional[str],
    phone: Optional[str],
    expected_init_kwargs: Dict,
    expected_start_kwargs: Dict,
    expected_error: Optional[Any],
):
    c = ClientConfig(
        client_type=client_type,
        flavor=flavor,
        session_string=session_string,
        session_file=sess_file,
        bot_token=token,
        phone_number=phone,
    )
    assert c.init_kwargs() == expected_init_kwargs
    assert c.start_kwargs() == expected_start_kwargs


class TestPyrogramClientConfig:
    @pytest.mark.parametrize(
        "client_type,flavor,session_string,sess_file,token,phone,expected_init_kwargs,expected_start_kwargs,"
        "expected_error",
        pyrogram_start_tests,
    )
    def test_pyrogram_bot_combinations(
        self,
        client_type: ClientType,
        flavor: SupportedLibraries,
        session_string: Optional[str],
        sess_file: Optional[str],
        token: Optional[str],
        phone: Optional[str],
        expected_init_kwargs: Dict,
        expected_start_kwargs: Dict,
        expected_error: Optional[Any],
        api_config,  # fixture
    ):
        conf = ClientConfig(
            client_type=client_type,
            flavor=flavor,
            session_string=session_string,
            session_file=sess_file,
            bot_token=token,
            phone_number=phone,
        )

        assert conf.effective_session_location_arg == "mysession"
        assert isinstance(conf.full_session_path, Path)
        assert conf.full_session_path == expected_session

        client = TelethonClient(**conf.init_kwargs(api_config=api_config))

        inputs_captured = []

        def capture_input(prompt: str):
            inputs_captured.append(prompt)
            if conf.client_type is ClientType.bot:
                return conf.bot_token
            elif conf.client_type is ClientType.user:
                return conf.phone_number
            else:
                pytest.fail()

        with mock.patch.object(telethon.client.auth, "input", capture_input):
            client.start(**conf.start_kwargs())

        assert inputs_captured


class TestTelethonClientConfig:
    @pytest.mark.parametrize(
        "client_type,flavor,session_string,sess_file,token,phone,expected_init_kwargs,expected_start_kwargs,"
        "expected_error",
        telethon_start_tests,
    )
    def test_telethon_bot_combinations(
        self,
        client_type: ClientType,
        flavor: SupportedLibraries,
        session_string: Optional[str],
        sess_file: Optional[str],
        token: Optional[str],
        phone: Optional[str],
        expected_init_kwargs: Dict,
        expected_start_kwargs: Dict,
        expected_error: Optional[Any],
        api_config,  # fixture
        monkeypatch,
    ):
        conf = ClientConfig(
            client_type=client_type,
            flavor=flavor,
            session_string=session_string,
            session_file=sess_file,
            bot_token=token,
            phone_number=phone,
        )

        init_kwargs = conf.init_kwargs()
        if exp_sess_str := expected_init_kwargs.pop("session", None):
            if isinstance(exp_sess_str, StringSession):
                act_sess_str = init_kwargs.pop("session", None)
                assert act_sess_str
                assert isinstance(act_sess_str, StringSession)
                assert act_sess_str.auth_key == exp_sess_str.auth_key

        assert init_kwargs == expected_init_kwargs
        assert conf.start_kwargs() == expected_start_kwargs

        client = TelethonClient(**conf.init_kwargs(api_config=api_config))

        inputs_captured = []

        def capture_input(prompt: str):
            inputs_captured.append(prompt)
            if conf.client_type is ClientType.bot:
                return conf.bot_token
            elif conf.client_type is ClientType.user:
                return conf.phone_number
            else:
                pytest.fail()

        # async def connect_patch(*args):
        #     print(args)

        class Success(Exception):
            pass

        async def _start_patch(phone, bot_token, **_kwargs):
            if conf.phone_number:
                assert phone == conf.phone_number
            else:
                assert callable(phone)
            if conf.bot_token:
                assert bot_token == conf.bot_token
            else:
                assert not bot_token
            raise Success

        # noinspection PyUnresolvedReferences
        assert client.session.server_address
        # noinspection PyUnresolvedReferences
        assert client.session.port
        # noinspection PyUnresolvedReferences
        assert client.session.dc_id

        with mock.patch.object(
            client, "_start", _start_patch,
        ):
            # with mock.patch.object(telethon.client.auth, "input", capture_input):
            try:
                client.start(**conf.start_kwargs())
            except Success:
                pass
            finally:
                client.disconnect()

        assert inputs_captured == []
