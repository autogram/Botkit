from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, cast
from uuid import UUID

from redis import Redis
from redis_collections import Dict as RedisDict

from ._base import (
    ICallbackManager,
    generate_id,
)
from ._base import CallbackActionContext

from logzero import logger as log

# TODO: Try use json instead of pickle? https://github.com/honzajavorek/redis-collections/issues/122
# Force pydantic models?


class RedisCallbackManager(ICallbackManager):
    def __init__(self, redis_client: Redis, key: str = "callbacks", maxsize: int = 30):
        self.callbacks: RedisDict[str, CallbackActionContext] = RedisDict(redis=redis_client, key=key + "_normaldict3")

        # self.callbacks: LRUDict[str, CallbackContext] = LRUDict(
        #     maxsize=maxsize, redis=redis_client, key=key
        # )

        now = datetime.now()
        to_remove: List[str] = []

        # pipe = self.redis if pipe is None else pipe
        # if isinstance(pipe, Pipeline):
        #     pipe.hgetall(self.key)
        #     items = pipe.execute()[-1].items()
        # else:
        #     items = self.redis.hgetall(self.key).items()
        #
        # return {self._unpickle_key(k): self._unpickle(v) for k, v in items}

        try:
            for k, v in self.callbacks.items():
                if not hasattr(v, "created"):
                    to_remove.append(k)
                elif cast(CallbackActionContext, v).created + timedelta(days=7) > now:
                    to_remove.append(k)

            for i in to_remove:
                self.callbacks.pop(i)
        except Exception as e:
            log.error(e)
            log.info("Recreating callbacks...")
            self.callbacks.clear()

    def create_callback(self, context: CallbackActionContext) -> str:
        id_ = generate_id()
        self.callbacks[id_] = context.dict()
        # self.callbacks.sync()
        return id_

    def lookup_callback(self, id_: Union[str, UUID]) -> Optional[CallbackActionContext]:
        context: Optional[Dict] = self.callbacks.get(str(id_))
        if context is None:
            return None
        return CallbackActionContext(**context)

    def clear(self):
        self.callbacks.clear()

    def force_sync(self):
        self.callbacks.sync()
