from typing import Any, Set, cast

from ..log import get_logger
from ..msg.client_to_server import ChatFromClient
from ..msg.server_to_client import ChatToClient
from .client import Client

_logger: Any = get_logger()


class ChatRoom:
    def __init__(self) -> None:
        self._clients: Set[Client] = set()

    def join(self, client: Client) -> None:
        _logger.debug("User joins group", client=client.name)
        self._clients.add(client)

    def leave(self, client: Client) -> None:
        _logger.debug("User leaves group", client=client.name)
        if client in self._clients:
            self._clients.remove(client)

    def send_message(self, msg: ChatFromClient, from_client: Client) -> None:
        _logger.debug("User sends message to group", from_client=from_client.name)
        for client in self._clients:
            out_msg = ChatToClient(cast(str, from_client.name), msg.message)
            if not (client is from_client):
                client.msg_sender.send(out_msg)

    @property
    def empty(self) -> bool:
        return not self._clients
