from ._base import ICallbackManager

# TODO: add proper try except for opt-in install of redis for callback management
import redis_collections
from ._redis import RedisCallbackManager


from ._local import LocalDictCallbackManager
from ._base import CallbackActionContext
from ._simple import create_callback, lookup_callback


__all__ = ["ICallbackManager", "RedisCallbackManager", "LocalDictCallbackManager", "CallbackActionContext",
           "lookup_callback", "create_callback"]

