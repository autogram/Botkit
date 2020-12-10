from unittest.mock import Mock

from injector import Injector
from lambdas import _
from redis import Redis

from botkit import botkit_settings
from botkit.persistence.callback_store import (
    ICallbackStore,
    MemoryDictCallbackStore,
    RedisCallbackStore,
    configure_callback_store,
)
from botkit.utils import nameof


def test_configure_callback_store():
    inj = Injector([configure_callback_store, lambda binder: binder.bind(Redis, to=Mock(Redis))])
    inj.get(RedisCallbackStore)
    inj.get(MemoryDictCallbackStore)

    cbs = inj.get(ICallbackStore)
    assert (
        type(cbs) == MemoryDictCallbackStore
    ), f"Default store was not {nameof(MemoryDictCallbackStore)}"

    botkit_settings.callback_store_qualifier = "memory"
    cbs = inj.get(ICallbackStore)
    assert type(cbs) == MemoryDictCallbackStore

    botkit_settings.callback_store_qualifier = "redis"
    cbs = inj.get(ICallbackStore)
    assert type(cbs) == RedisCallbackStore

    botkit_settings.callback_store_qualifier = "memory"
    cbs = inj.get(ICallbackStore)
    assert type(cbs) == MemoryDictCallbackStore
