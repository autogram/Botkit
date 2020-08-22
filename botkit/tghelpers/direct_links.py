from enum import IntEnum

from pyrogram import Message, User, Chat, Client
from pyrogram.api.types import Channel
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
    else:
        if not isinstance(peer, User):
            peer_id = peer.id
            if isinstance(peer, Channel):
                return f"https://t.me/c/{peer_id}"
            invite_link = _links_cache.get(peer_id, None)
            if not invite_link:
                invite_link = (await client.get_chat(peer_id)).invite_link
                _links_cache[peer_id] = invite_link
            if invite_link:
                return cast(str, invite_link)

        if platform == Platform.android:
            return f"tg://openmessage?user_id={peer.id}"
        elif platform == Platform.ios:
            return f"t.me/@{peer.id}"
        elif platform == Platform.web:
            # TODO: maybe incorrect, test!
            return f"https://web.Telegram.org/#/im?p=u{peer.id}"
        else:
            raise ValueError(
                f"_IdentifiableUser has no username, creating direct link on platform {platform} not possible."
            )
