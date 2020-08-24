import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional, Union, cast
from uuid import UUID

from redis import Redis
from redis_collections import Dict as RedisDict, LRUDict

from ._base import (
    ICallbackManager,
    generate_id,
)
from ._base import CallbackActionContext

from logzero import logger as log

# TODO: Try use json instead of pickled dicts? https://github.com/honzajavorek/redis-collections/issues/122
# TODO: Force pydantic models?


class RedisCallbackManager(ICallbackManager):
    def __init__(
        self,
        redis_client: Redis,
        key: str = "callbacks",
        storage_type: Literal["lru", "normal"] = "normal",
        maxsize: int = 2000,
    ):
        """

        :param redis_client:
        :type redis_client:
        :param key:
        :type key:
        :param storage_type:
        :type storage_type:
        :param maxsize: Ignored if storage_type is "normal".
        :type maxsize:
        """
        # TODO: Add documentation that lru should be used in production
        if storage_type == "lru":
            self.callbacks: LRUDict[str, Dict] = LRUDict(
                maxsize=maxsize, redis=redis_client, key=key + "_lru_dict"
            )
        elif storage_type == "normal":
            self.callbacks: RedisDict[str, Dict] = RedisDict(
                redis=redis_client, key=key + "_normal_dict"
            )

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

    def remove_outdated(self, days: int = 7):
        now = datetime.utcnow()
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
                if "created" not in v:
                    print("created not in v")
                    to_remove.append(k)
                elif v.get("created") + timedelta(days=7) <= now:
                    to_remove.append(k)

            for i in to_remove:
                self.callbacks.pop(i)

            if (num_removed := len(to_remove)) > 0:
                log.info(f"Dropped {num_removed} outdated callbacks.")
        except Exception as e:
            log.error(e)
            log.info("Recreating callbacks...")
            self.callbacks.clear()
