import binascii

import pytest
from telethon.sessions import StringSession

from botkit.configuration import *

TOKEN = "123456789:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
PHONE_NUMBER = "+49123456789"
SESS_STR = "123AF" * 15
PYROGRAM_SESS_STR = (
    "111111111111111111111111111111111111111111111111111111111111111111111111111111111-iYNF7EhMbE8"
    "l25oA5UYcG8X-8EcE7W6V3cEAgNPlXP5_evlyfdkQ8b_2lsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA-j72ZVCUV9U"
    "_ER5KqXtViESAsnAeeSqd3aPGcERmEjg54nI0Am_oDrMPhNP1VuEcFunrsUwdkf7YA7LmgQA"
)
TELETHON_SESS_STR = (
    "1111111111111111111111111111111111111111111111111111-WW6LA0ac4z2TGyrRY3eSO6Us1ZUywxzzxFR27yZO"
    "zE3lhaRDqE5qUhoh1YUdM4hP_knjLFDM9IcrOEbbO7mgrG72Ty5Y69HBeNkGZ2-9wuLO2-FNjUsq1hNYlaDqaPMqg7dQT"
    "QL8isHkRoqyyxaxkP1JOdFp-XVRxsuvj00VdDxox6qBfmBlZOvGkqliNIdtkSsrU1gCxJAvN24QyJppS7lhM-gxUk70yD"
    "HK5Yl63Ep0THPnPOYm9adYGvpA5qYq49s2_oQFUeLlhnlUUq_X2HtyAc5yH857u0RMo8EJm5o="
)

test_configs = {
    "pyrogram": [
        (
            ClientType.bot,
            "pyrogram",
            None,
            "mysession",
            TOKEN,
            None,
            {"bot_token": TOKEN, "phone_number": None, "session_name": "mysession.session"},
            dict(),
            None,
        ),
        (ClientType.bot, "pyrogram", None, "mysession", None, None, dict(), dict(), None),
        (ClientType.bot, "pyrogram", SESS_STR, None, None, None, dict(), dict(), None),
        (ClientType.bot, "pyrogram", None, None, None, None, dict(), dict(), None),
        (ClientType.user, "pyrogram", SESS_STR, "mysession", None, None, dict(), dict(), None,),
        (ClientType.user, "pyrogram", None, "mysession", None, None, dict(), dict(), None),
        (ClientType.user, "pyrogram", SESS_STR, None, None, None, dict(), dict(), None),
        (ClientType.user, "pyrogram", None, None, None, None, dict(), dict(), None),
    ],
    "telethon": [
        (
            ClientType.bot,
            "telethon",
            TELETHON_SESS_STR,
            "mysession",
            None,
            None,
            dict(session=StringSession(TELETHON_SESS_STR)),
            dict(),
            binascii.Error,
        ),
        (ClientType.bot, "telethon", None, "mysession", None, None, dict(), dict(), None),
        (ClientType.bot, "telethon", TELETHON_SESS_STR, None, None, None, dict(), dict(), None),
        (ClientType.bot, "telethon", None, None, None, None, dict(), dict(), None),
        (
            ClientType.user,
            "telethon",
            TELETHON_SESS_STR,
            "mysession",
            None,
            None,
            dict(),
            dict(),
            None,
        ),
        (ClientType.user, "telethon", None, "mysession", None, None, dict(), dict(), None),
        (ClientType.user, "telethon", TELETHON_SESS_STR, None, None, None, dict(), dict(), None),
        (ClientType.user, "telethon", None, None, None, None, dict(), dict(), None),
    ],
}


pyrogram_start_tests = [pytest.param(*c) for c in test_configs["pyrogram"]]
telethon_start_tests = [pytest.param(*c) for c in test_configs["telethon"]]

all_libs_test_configs = test_configs["pyrogram"] + test_configs["telethon"]
