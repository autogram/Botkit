import asyncio
import pytz
import logging
import logzero
from datetime import datetime, timedelta
from pydantic import BaseModel
from pyrogram import Client
from typing import Literal
from typing import Optional, Union, List
from typing import cast

from pyrogram.types import Message
from typing_extensions import AsyncGenerator

from botkit.builtin_modules.system.sytem_management_module import ToggleSystemStateCommand
from botkit.builtin_services.eventing import command_bus


class Ping(BaseModel):
    ping_time: datetime
    env: str


class StatusPings:
    def __init__(
        self,
        client: Client,
        log_chat: Union[int, str],
        environment: str,
        environment_priority: List[str],
    ):
        self.log_chat = log_chat
        self.environment = environment
        self.client = client
        self.ping_interval: int = 6
        self.reactivate_after_seconds: int = 20  # minimum 20
        self.last_sent_ping: Optional[Ping] = None
        self.last_ping_msg: Optional[Message] = None
        self.priority = environment_priority
        self.status: Literal["active", "waiting"] = "active"
        self.log = logzero.setup_logger(self.__class__.__name__, level=logging.INFO)

    def run(self) -> None:
        asyncio.ensure_future(self.ping_loop())

    async def ping_loop(self):
        while True:
            try:
                queried_ping: Optional[Ping] = await self.query_most_recent_ping()

                other_detected = (
                    self.other_instance_detected(queried_ping, own_environment=self.environment)
                    if queried_ping
                    else False
                )
                await self.update_status(queried_ping, other_detected)

                if self.status == "active":
                    await self._send_ping(force_resend=queried_ping is None)
            except Exception:
                self.log.exception("Error during ping loop.")
            finally:
                await asyncio.sleep(self.ping_interval)

    async def update_status(self, queried_ping: Optional[Ping], other_detected: bool):
        if self.status == "active":
            if not queried_ping:
                self.log.warning(
                    "We were looking for pings but couldn't find any even though the system is active. "
                    "Probably a bug."
                )
                return
            if other_detected:
                if self.has_higher_priority(queried_ping.env, compare_to=self.environment):
                    command = ToggleSystemStateCommand(
                        new_state="pause",
                        triggered_by=self.__class__.__name__,
                        reason_phrase=f"Another instance in environment {queried_ping.env} came online and it has a "
                        f"higher priority.",
                    )
                    command_bus.execute(command)
                    self.status = "waiting"
                    return
        elif self.status == "waiting":
            if not queried_ping:
                command = ToggleSystemStateCommand(
                    new_state="unpause",
                    triggered_by=self.__class__.__name__,
                    reason_phrase=f"Could not find any ping messages.",
                )
                command_bus.execute(command)
                self.status = "active"
                return

            if self.has_higher_priority(self.environment, compare_to=queried_ping.env):
                command = ToggleSystemStateCommand(
                    new_state="unpause",
                    triggered_by=self.__class__.__name__,
                    reason_phrase=f"The other currently-active instance in environment {queried_ping.env} hast a lower "
                    f"priority {self.environment}.",
                )
                command_bus.execute(command)
                self.status = "active"
                return

            # Waiting for all other instances to be offline for some time
            if self.timestamp_older_than(
                queried_ping.ping_time, seconds=self.reactivate_after_seconds
            ):
                command = ToggleSystemStateCommand(
                    new_state="unpause",
                    triggered_by=self.__class__.__name__,
                    reason_phrase=f"The environment {queried_ping.env} went offline.",
                )
                command_bus.execute(command)
                self.status = "active"
            elif self.timestamp_between(
                queried_ping.ping_time,
                self.reactivate_after_seconds - (self.ping_interval * 2),
                self.reactivate_after_seconds - self.ping_interval,
            ):
                self.log.info(
                    f"Instance in {queried_ping.env} environment seems to be going down. "
                    f"{self.environment} ready to take over."
                )
            else:
                self.log.debug(
                    f"Paused since another instance with higher priority ({queried_ping.env}) is running."
                )

    def has_higher_priority(self, env: str, compare_to: str) -> Optional[bool]:
        try:
            return self.priority.index(env) < self.priority.index(compare_to)
        except ValueError:
            self.log.exception(
                f"Environment priority map does not contain '{env}' and '{compare_to}'."
            )
            return None

    async def query_most_recent_ping(self) -> Optional[Ping]:
        found = None
        async for m in cast(
            AsyncGenerator[Message, None], self.client.iter_history(self.log_chat, limit=10),
        ):
            if not m.text.startswith("{"):
                continue
            try:
                queried_ping = Ping.parse_raw(m.text)
            except:
                queried_ping = None

            if queried_ping:
                # save the match if it's the first
                if not found:
                    self.last_ping_msg = m
                    found = queried_ping
                    continue

                # clean up
                try:
                    await m.delete()
                except:
                    pass
        return found

    @staticmethod
    def other_instance_detected(received_ping: Ping, own_environment: str) -> bool:
        return received_ping.env != own_environment

    @staticmethod
    def timestamp_older_than(dt: datetime, seconds: int) -> bool:
        now = datetime.now(tz=pytz.UTC)
        result = now > (dt + timedelta(seconds=seconds))
        return result

    @staticmethod
    def timestamp_between(dt: datetime, min_seconds: int, max_seconds: int):
        return (
            dt + timedelta(max_seconds)
            > datetime.now(tz=pytz.UTC)
            > dt + timedelta(seconds=min_seconds)
        )

    async def _send_ping(self, force_resend: bool = False):
        self.last_sent_ping = Ping(env=self.environment, ping_time=datetime.now(tz=pytz.UTC))

        if self.last_ping_msg and not force_resend:
            try:
                self.last_ping_msg = await self.client.edit_message_text(
                    self.log_chat, self.last_ping_msg.message_id, self.last_sent_ping.json(),
                )
                return
            except:
                pass
        self.last_ping_msg = await self.client.send_message(
            self.log_chat, self.last_sent_ping.json()
        )
