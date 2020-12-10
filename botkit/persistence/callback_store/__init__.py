from typing import Union

from injector import Binder, inject

from ._base import CallbackActionContext, ICallbackStore
from ._local import MemoryDictCallbackStore
from ._redis import RedisCallbackStore, RedisClientUnavailableException
from ._simple import create_callback, lookup_callback

try:
    from redis import Redis
except:
    pass

from botkit import botkit_settings

__all__ = [
    "ICallbackStore",
    "RedisCallbackStore",
    "MemoryDictCallbackStore",
    "lookup_callback",
    "create_callback",
]


ran = []  # TODO: hack


def configure_callback_store(binder: Binder) -> None:
    @inject
    def select_callback_store_impl(
        redis: RedisCallbackStore, memory: MemoryDictCallbackStore
    ) -> Union[RedisCallbackStore, MemoryDictCallbackStore]:
        if botkit_settings.callback_store_qualifier == "redis":
            if not ran:
                redis.remove_outdated(botkit_settings.callbacks_ttl_days)
                ran.append(True)
            return redis

        if botkit_settings.callback_store_qualifier == "memory":
            return memory

        return memory

    binder.bind(MemoryDictCallbackStore)
    binder.bind(RedisCallbackStore)
    binder.bind(ICallbackStore, to=select_callback_store_impl)
