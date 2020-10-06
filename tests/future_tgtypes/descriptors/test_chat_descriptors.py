from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from botkit.clients.client import IClient
from botkit.future_tgtypes.descriptors.chat_descriptor import ChatDescriptor
from botkit.future_tgtypes.identities.chat_identity import ChatIdentity

pytestmark = pytest.mark.asyncio

fields = {"chat_id": 123, "username": "@testing", "title_regex": ".*abc.*"}

# region basic field tests


def test_no_fields_set_raises_value_error():
    with pytest.raises(ValueError, match=r".*at least one.*"):
        ChatDescriptor()


def test_invalid_username_raises_validation_error():
    with pytest.raises(ValidationError, match=r"does not match regex"):
        ChatDescriptor(username="@kek tus")


def test_basic():
    c = ChatDescriptor(username="@henlo")
    assert c.username == "@henlo"


def test_any_field_set_no_error():
    for k, v in fields.items():
        kwargs = {k: v}
        c = ChatDescriptor(**kwargs)
        assert c.at_least_one(kwargs)
        assert getattr(c, k, None) == v


# endregion


# region lookup unit tests


@pytest.fixture(scope="module")
def mocked_client() -> Mock[IClient]:
    return Mock(IClient)


async def test_basic_lookup(mocked_client):
    cd = ChatDescriptor(username="@josxa")
    res = await cd.resolve(mocked_client)

    assert isinstance(res, ChatIdentity)


# endregion
