from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import sys
from pyrogram.filters import Filter, create
from pyrogram.types import Message, MessageEntity
from typing_extensions import Literal

MessageEntityType = Literal[
    "mention",
    "hashtag",
    "cashtag",
    "bot_command",
    "url",
    "email",
    "bold",
    "italic",
    "code",
    "pre",
    "underline",
    "strike",
    "blockquote",
    "text_link",
    "text_mention",
    "phone_number",
]


def parse_entity_text(entity: MessageEntity, message_text: str) -> str:
    # Is it a narrow build, if so we don't need to convert
    if sys.maxunicode == 0xFFFF:
        return message_text[entity.offset : entity.offset + entity.length]
    else:
        entity_text = message_text.encode("utf-16-le")
        entity_text = entity_text[entity.offset * 2 : (entity.offset + entity.length) * 2]

        return entity_text.decode("utf-16-le")


@dataclass
class ParsedEntity:
    entity: MessageEntity
    text: str


def parse_entities(
    message: Message, types: Union[List[MessageEntityType], MessageEntityType] = None
) -> List[ParsedEntity]:
    if types is None:
        types = MessageEntity.ENTITIES.values()
    elif isinstance(types, str):
        types = [types]

    return [
        ParsedEntity(entity=entity, text=parse_entity_text(entity, message.text))
        for entity in message.entities or []
        if entity.type in types
    ]


def create_entity_filter(type_: MessageEntityType) -> Filter:
    return create(
        lambda _, __, m: any(parse_entities(m, type_)) if m.entities else False, type_.upper(),
    )


class EntityFilters:
    url = create_entity_filter("url")
    text_link = create_entity_filter("text_link")
