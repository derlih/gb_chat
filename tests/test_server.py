from unittest.mock import MagicMock

import pytest
from gb_chat.server.client import Client
from gb_chat.server.server import Server


@pytest.fixture
def client():
    return MagicMock(spec_set=Client)


@pytest.fixture
def sut():
    return Server()


def test_client_connected(sut, client):
    sut.on_client_connected(client)


def test_disconnected_not_authed_client(sut, client):
    sut.on_client_connected(client)
    sut.on_client_disconnected(client)
