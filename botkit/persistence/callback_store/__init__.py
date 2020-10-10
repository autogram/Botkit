from ._base import ICallbackStore, CallbackActionContext

# TODO: add proper try except for opt-in install of redis for callback management
import redis_collections

from ._redis import RedisCallbackStore
from ._local import MemoryDictCallbackStore
from ._simple import create_callback, lookup_callback


__all__ = [
    "ICallbackStore",
    "RedisCallbackStore",
    "MemoryDictCallbackStore",
    "lookup_callback",
    "create_callback",
]
