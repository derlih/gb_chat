from unittest.mock import MagicMock

import pytest
from gb_chat.common.exceptions import InvalidRoomName
from gb_chat.common.room_name_validator import RoomNameValidator
from gb_chat.io.message_sender import MessageSender
from gb_chat.server.chat_room import ChatRoom
from gb_chat.server.chat_room_manager import ChatRoomManager
from gb_chat.server.client import Client
from gb_chat.server.disconnector import Disconnector


@pytest.fixture
def chat_room():
    return MagicMock(spec_set=ChatRoom)


@pytest.fixture
def chat_room_factory(chat_room):
    return MagicMock(side_effect=[chat_room])


@pytest.fixture
def room_name_validator():
    res = MagicMock(spec_set=RoomNameValidator)
    res.is_valid.return_value = True
    return res


@pytest.fixture
def sut(room_name_validator, chat_room_factory):
    return ChatRoomManager(room_name_validator, chat_room_factory)


@pytest.fixture
def client1():
    return Client(
        MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector), "username1"
    )


@pytest.fixture
def client2():
    return Client(
        MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector), "username2"
    )


def test_join_raises_when_invalid_name(sut, room_name_validator, client1):
    room_name_validator.is_valid.return_value = False

    with pytest.raises(InvalidRoomName):
        sut.join("#room", client1)

    room_name_validator.is_valid.assert_called_once_with("#room")


def test_join_creates_room_when_first_user(sut, chat_room_factory, chat_room, client1):
    sut.join("#room", client1)

    chat_room_factory.assert_called_once_with()
    chat_room.join.assert_called_once_with(client1)


@pytest.fixture
def sut_with_room(sut, chat_room_factory, chat_room, client1):
    sut.join("#room", client1)
    chat_room_factory.reset_mock()
    chat_room.join.reset_mock()
    return sut


def test_join_creates_room_when_first_user(
    sut_with_room, chat_room_factory, chat_room, client2
):
    sut_with_room.join("#room", client2)

    chat_room_factory.assert_not_called()
    chat_room.join.assert_called_once_with(client2)


def test_leave_does_nothing_when_no_room(sut, client1):
    sut.leave("#room", client1)


def test_leave_remove_room(sut_with_room, chat_room_factory, chat_room, client1):
    sut_with_room.leave("#room", client1)

    chat_room.leave.assert_called_once_with(client1)

    # check that needs to create
    chat_room_factory.side_effect = None
    sut_with_room.join("#room", client1)

    chat_room_factory.assert_called_once_with()


def test_leave_all(sut_with_room, chat_room_factory, chat_room, client1):
    sut_with_room.leave_all(client1)
    chat_room.leave.assert_called_once_with(client1)

    # check that needs to create
    chat_room_factory.side_effect = None
    sut_with_room.join("#room", client1)

    chat_room_factory.assert_called_once_with()
