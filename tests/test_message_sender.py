from unittest.mock import MagicMock

import pytest
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.serializer import Serializer
from gb_chat.msg.client_to_server import (Authenticate, Chat, Join, Leave,
                                          Presence, Quit)
from gb_chat.msg.server_to_client import Probe, Response
from gb_chat.msg.status import Status


@pytest.mark.parametrize(
    "msg,expected",
    [
        (
            Response(100, "message text"),
            {"response": 100, "message": "message text", "time": 123},
        ),
        (Probe(), {"action": "probe", "time": 123}),
        (
            Authenticate("user_name", "pass"),
            {
                "action": "authenticate",
                "time": 123,
                "user": {"account_name": "user_name", "password": "pass"},
            },
        ),
        (Quit(), {"action": "quit"}),
        (Presence(), {"action": "presence", "time": 123}),
        (
            Presence(Status.ONLINE),
            {"action": "presence", "time": 123, "status": "online"},
        ),
        (
            Chat("recipient", "message text"),
            {
                "action": "msg",
                "time": 123,
                "to": "recipient",
                "message": "message text",
            },
        ),
        (Join("#room_name"), {"action": "join", "room": "#room_name", "time": 123}),
        (Leave("#room_name"), {"action": "leave", "room": "#room_name", "time": 123}),
    ],
)
def test_send(msg, expected):
    serializer = MagicMock(spec_set=Serializer)
    sut = MessageSender(serializer, MagicMock(return_value=123))
    sut.send(msg)
    serializer.serialize.assert_called_once_with(expected)
