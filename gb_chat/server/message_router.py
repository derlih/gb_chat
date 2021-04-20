from ..msg.client_to_server import (Authenticate, Chat, ClientToServerMessage,
                                    Join, Leave, Presence, Quit)
from .server import Server


class UnsupportedMessage(ValueError):
    pass


class MessageRouter:
    def __init__(self, server: Server) -> None:
        self._server = server

    def route(self, msg: ClientToServerMessage) -> None:
        if isinstance(msg, Authenticate):
            self._server.on_auth(msg)
        elif isinstance(msg, Quit):
            self._server.on_quit(msg)
        elif isinstance(msg, Presence):
            self._server.on_presense(msg)
        elif isinstance(msg, Chat):
            self._server.on_chat(msg)
        elif isinstance(msg, Join):
            self._server.on_join(msg)
        elif isinstance(msg, Leave):
            self._server.on_leave(msg)
        else:
            raise UnsupportedMessage(f"Unsupported message {type(msg)}")
