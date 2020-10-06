from enum import IntEnum

from pyrogram import Client
from pyrogram.raw.types import Channel
from pyrogram.types import Message, User, Chat
from typing import Optional, Union, cast, Dict

_links_cache: Dict[int, str] = {}


class Platform(IntEnum):
    android = 1
    ios = 2
    web = 3
    desktop = 4


async def direct_link_to_message(
    reference: Message, platform: Optional[Platform] = Platform.android
) -> str:
    entity_link = await direct_link(reference._client, reference.chat, platform)
    return f"{entity_link}/{reference.message_id}"


async def direct_link(
    client: Client,
    peer: Union[User, Chat, Channel],
    platform: Optional[Platform] = Platform.android,
) -> str:
    if peer.username:
        return f"https://t.me/{peer.username}"

    if isinstance(peer, User):
        return direct_link_user(peer, platform)

    peer_id = peer.id
    if isinstance(peer, Channel):
        return f"https://t.me/c/{peer_id}"
    invite_link: str = _links_cache.get(peer_id, None)
    if not invite_link:
        invite_link: str = (await client.get_chat(peer_id)).invite_link
        _links_cache[peer_id] = invite_link
    if invite_link:
        return invite_link


def direct_link_user(user: User, platform: Optional[Platform] = Platform.android):
    if user.username:
        return f"https://t.me/{user.username}"

    if platform == Platform.android:
        return f"tg://openmessage?user_id={user.id}"
    elif platform == Platform.ios:
        return f"t.me/@{user.id}"
    elif platform == Platform.web:
        # TODO: maybe incorrect, test!
        return f"https://web.Telegram.org/#/im?p=u{user.id}"
    else:
        raise ValueError(
            f"User has no username, creating direct link on platform {platform} not possible."
        )
