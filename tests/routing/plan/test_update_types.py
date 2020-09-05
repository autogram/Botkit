from typing import Callable, List, Union

from pyrogram import Client
from pyrogram.types import CallbackQuery, Message

from botkit.libraries.annotations import IClient
from botkit.libraries.pyro_types._pyrogram_update_type_inference import (
    determine_pyrogram_handler_update_types,
)
from botkit.routing.update_types.updatetype import UpdateType
from botkit.utils.typed_callable import TypedCallable


def make_valid_handler_variations(update_type: object) -> List[Callable]:
    async def pure(client: IClient, message: update_type):
        pass

    async def pure_pyro(client: Client, message: update_type):
        pass

    async def no_client_annotation(client, x: update_type):
        pass

    async def with_additional_args(
        client, message: update_type, additional_arg: int = None
    ):
        pass

    async def more_args_inbetween(client, something, sth_else, message: update_type):
        pass

    def sync(client, message: update_type):
        pass

    return [
        pure,
        pure_pyro,
        no_client_annotation,
        with_additional_args,
        more_args_inbetween,
        sync,
    ]


def test_message_handler_can_be_determined() -> None:
    handlers = make_valid_handler_variations(Message)

    for h in handlers:
        res = determine_pyrogram_handler_update_types(TypedCallable(h))

        assert res == {UpdateType.message}


def test_message_callback_query_union_handler_can_be_determined() -> None:
    handlers = make_valid_handler_variations(Union[Message, CallbackQuery])

    for h in handlers:
        res = determine_pyrogram_handler_update_types(TypedCallable(h))

        assert res == {UpdateType.message, UpdateType.callback_query}
