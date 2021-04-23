from http import HTTPStatus
from typing import Any, Dict, List

from ..common.room_name_validator import RoomNameValidator
from ..log import get_logger
from ..msg.client_to_server import (Authenticate, ChatFromClient, Join, Leave,
                                    Presence, Quit)
from ..msg.server_to_client import ChatToClient, Probe, Response
from .auth_clients_holder import AuthClientsHolder
from .client import Client

_logger: Any = get_logger()


class Server:
    auth = AuthClientsHolder()

    def __init__(self) -> None:
        self._clients: List[Client] = []

    def send_probes(self) -> None:
        _logger.debug("Send probes")
        for client in self.auth.all:
            client.msg_sender.send(Probe())

    def on_client_connected(self, client: Client) -> None:
        _logger.info("Client connected")
        self._clients.append(client)

    def on_client_disconnected(self, client: Client) -> None:
        _logger.info("Client disconnected")
        self._clients.remove(client)
        if self.auth.is_authed(client):
            self.auth.remove_client(client)

    def on_auth(self, msg: Authenticate, from_client: Client) -> None:
        _logger.debug("Auth received")
        from_client.name = msg.login
        self.auth.add_client(from_client)
        from_client.msg_sender.send(Response(HTTPStatus.OK, "Login successful"))

    def on_quit(self, msg: Quit, from_client: Client) -> None:
        _logger.debug("Quit received")
        from_client.disconnector.disconnect()

    @auth.required
    def on_presence(self, msg: Presence, from_client: Client) -> None:
        if not msg.status:
            _logger.debug("Presence without status received")
            return

        _logger.info("Set presence", presence=msg.status.value)

    @auth.required
    def on_chat(self, msg: ChatFromClient, from_client: Client) -> None:
        to_client = self.auth.find_client(msg.to)
        if to_client is None:
            _logger.warning("Chat message for not authed client", to=msg.to)
            return

        if from_client.name == msg.to:
            _logger.warning("Chat message for self", to=msg.to)
            return

        to_client.msg_sender.send(ChatToClient(from_client.name, msg.message))

    @auth.required
    def on_join(self, msg: Join, from_client: Client) -> None:
        pass

    @auth.required
    def on_leave(self, msg: Leave, from_client: Client) -> None:
        pass
