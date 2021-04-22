from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from gb_chat.common.room_name_validator import RoomNameValidator
from gb_chat.io.message_sender import MessageSender
from gb_chat.msg.client_to_server import (Authenticate, ChatFromClient,
                                          Presence, Quit)
from gb_chat.msg.server_to_client import ChatToClient, Probe, Response
from gb_chat.msg.status import Status
from gb_chat.server.client import Client
from gb_chat.server.disconnector import Disconnector
from gb_chat.server.server import Server


@pytest.fixture
def client():
    return Client(MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector))


@pytest.fixture
def room_name_validator():
    return MagicMock(spec_set=RoomNameValidator)


@pytest.fixture
def sut(room_name_validator):
    return Server(room_name_validator)


def test_client_connected(sut, client):
    sut.on_client_connected(client)


@pytest.fixture
def sut_with_client(sut, client):
    sut.on_client_connected(client)
    return sut


def test_disconnected_not_authed_client(sut_with_client, client):
    sut_with_client.on_client_disconnected(client)


def test_send_response_when_receive_auth_request(sut_with_client, client):
    sut_with_client.on_auth(Authenticate("username", "password"), client)
    assert client.name == "username"
    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.OK, "Login successful")
    )


@pytest.fixture
def sut_with_authed_client(sut_with_client, client):
    sut_with_client.on_auth(Authenticate("username", "password"), client)
    client.msg_sender.send.reset_mock()
    return sut_with_client


def test_disconnected_authed_client(sut_with_authed_client, client):
    sut_with_authed_client.on_client_disconnected(client)


def test_not_send_probes_when_not_authed(sut_with_client, client):
    sut_with_client.send_probes()
    client.msg_sender.send.assert_not_called()


def test_not_send_probes_when_not_authed(sut_with_authed_client, client):
    sut_with_authed_client.send_probes()
    client.msg_sender.send.assert_called_once_with(Probe())


def test_disconnect_client_on_quit_msg(sut_with_client, client):
    sut_with_client.on_quit(Quit(), client)
    client.disconnector.disconnect.assert_called_once_with()


def test_on_chat_disconnect_on_msg_from_not_authed(sut_with_client, client):
    sut_with_client.on_chat(ChatFromClient("username", "msg"), client)
    client.disconnector.disconnect.assert_called_once()


def test_on_chat_ignores_msg_to_self(sut_with_authed_client, client):
    sut_with_authed_client.on_chat(ChatFromClient(client.name, "msg"), client)
    client.msg_sender.send.assert_not_called()


def test_on_presence_disconnect_on_msg_from_not_auth(sut_with_client, client):
    sut_with_client.on_presence(Presence(Status.ONLINE), client)
    client.disconnector.disconnect.assert_called_once()


def test_on_presence(sut_with_authed_client, client):
    sut_with_authed_client.on_presence(Presence(Status.ONLINE), client)
    client.disconnector.disconnect.assert_not_called()


@pytest.fixture
def client2():
    return Client(MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector))


@pytest.fixture
def sut_with_client2(sut_with_authed_client, client2):
    sut_with_authed_client.on_client_connected(client2)
    return sut_with_authed_client


def test_on_chat_ignores_msg_to_not_authed(sut_with_client2, client, client2):
    sut_with_client2.on_chat(ChatFromClient("to name", "msg"), client)
    client2.msg_sender.send.assert_not_called()


@pytest.fixture
def sut_with_two_authed_clients(sut_with_client2, client2):
    sut_with_client2.on_auth(Authenticate("username2", "password"), client2)
    assert client2.name == "username2"
    client2.msg_sender.send.reset_mock()
    return sut_with_client2


def test_on_chat_send_message_to_client(sut_with_two_authed_clients, client, client2):
    sut_with_two_authed_clients.on_chat(
        ChatFromClient(client2.name, "message text"), client
    )
    client2.msg_sender.send.assert_called_once_with(
        ChatToClient(client.name, "message text")
    )
