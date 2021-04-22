from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from gb_chat.io.message_sender import MessageSender
from gb_chat.msg.client_to_server import Authenticate, Quit
from gb_chat.msg.server_to_client import Probe, Response
from gb_chat.server.client import Client
from gb_chat.server.disconnector import Disconnector
from gb_chat.server.server import Server


@pytest.fixture
def client():
    return Client(MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector))


@pytest.fixture
def sut():
    return Server()


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
