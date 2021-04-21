from ..common.exceptions import UnsupportedMessageType
from ..msg.server_to_client import Probe, Response, ServerToClientMessage
from .client import Client


class MessageRouter:
    def __init__(self, client: Client) -> None:
        self._client = client

    def route(self, msg: ServerToClientMessage) -> None:
        if isinstance(msg, Response):
            self._client.on_response(msg)
        elif isinstance(msg, Probe):
            self._client.on_probe(msg)
        else:
            raise UnsupportedMessageType(f"Unsupported message {type(msg)}")
