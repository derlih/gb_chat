from typing import Dict, List

from ..msg.client_to_server import (Authenticate, Chat, Join, Leave, Presence,
                                    Quit)
from .client import Client


class Server:
    def __init__(self) -> None:
        self._clients: List[Client] = []
        self._auth_clients: Dict[str, Client] = {}

    def on_client_connected(self, client: Client) -> None:
        self._clients.append(client)

    def on_client_disconnected(self, client: Client) -> None:
        self._clients.remove(client)
        for name, auth_client in self._auth_clients.items():
            if auth_client is not client:
                continue

            del self._auth_clients[name]
            return

    def on_auth(self, msg: Authenticate) -> None:
        pass

    def on_quit(self, msg: Quit) -> None:
        pass

    def on_presense(self, msg: Presence) -> None:
        pass

    def on_chat(self, msg: Chat) -> None:
        pass

    def on_join(self, msg: Join) -> None:
        pass

    def on_leave(self, msg: Leave) -> None:
        pass
