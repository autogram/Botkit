from dataclasses import dataclass
from typing import Literal, Optional

from logzero import LogFormatter


_BOTKIT_DEFAULT_LOG_LEVEL = "INFO"


@dataclass
class _BotkitSettings:
    # region General

    application_name: str = "Botkit"

    # endregion

    # region Builder classes

    route_builder_class = None

    # endregion

    # region Callback manager

    callback_manager_qualifier: Literal["memory", "redis"] = "memory"
    """
    Qualifier key of the kind of callback manager to be used. Should be "memory" for an in-memory store (without
    persistence) and "redis" if you have the `redis_collections` package installed.

    If you want to use Redis, you will need to supply Botkit with a Redis client. This is done by exposing it to haps
    by using `@egg` and usually a `@scope(SINGLETON_SCOPE)`. The following example illustrates this:

    ```
    from decouple import config
    from haps import SINGLETON_SCOPE, egg, scope
    from redis import Redis

    @egg
    @scope(SINGLETON_SCOPE)
    def create_redis_client() -> Redis:
    return Redis(host=config("REDIS_HOST"), password=config("REDIS_PASSWORD"))
    ```
    """

    callbacks_ttl_days: int = 7
    """ abc """

    # endregion

    # region Logging

    _current_log_level: str = _BOTKIT_DEFAULT_LOG_LEVEL
    log_formatter = LogFormatter(
        fmt="%(color)s[%(levelname)1.1s %(asctime)s %(name)s:%(lineno)d]%(end_color)s %(message)s"
    )

    @property
    def log_level(self) -> str:
        return self._current_log_level

    @log_level.setter
    def log_level(self, value: Optional[str]) -> None:
        value = value or _BOTKIT_DEFAULT_LOG_LEVEL
        self._current_log_level = value

    # endregion


botkit_settings = _BotkitSettings()
