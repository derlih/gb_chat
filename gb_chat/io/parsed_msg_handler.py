from http import HTTPStatus
from typing import Optional, Union, cast

from ..client.message_router import MessageRouter as ClientMessageRouter
from ..msg.client_to_server import (Authenticate, Chat, Join, Leave, Presence,
                                    Quit)
from ..msg.server_to_client import Probe, Response
from ..msg.status import Status
from ..server.message_router import MessageRouter as ServerMessageRouter
from .json import JSON


class ParsedMessageHandler:
    def __init__(
        self, msg_router: Union[ServerMessageRouter, ClientMessageRouter]
    ) -> None:
        self._msg_router = msg_router

    def process(self, msg: JSON) -> None:
        if isinstance(self._msg_router, ServerMessageRouter):
            self._process_incomming_server_msg(msg)
        else:
            self._process_incomming_client_msg(msg)

    def _process_incomming_server_msg(self, msg: JSON) -> None:
        router = cast(ServerMessageRouter, self._msg_router)
        action = msg["action"]
        if action == "authenticate":
            user = msg["user"]
            router.route(Authenticate(user["account_name"], user["password"]))
        elif action == "quit":
            router.route(Quit())
        elif action == "presence":
            status: Optional[Status] = None
            if "status" in msg:
                status = Status(msg["status"])
            router.route(Presence(status))
        elif action == "msg":
            router.route(Chat(msg["to"], msg["message"]))
        elif action == "join":
            router.route(Join(msg["room"]))
        elif action == "leave":
            router.route(Leave(msg["room"]))

    def _process_incomming_client_msg(self, msg: JSON) -> None:
        router = cast(ClientMessageRouter, self._msg_router)
        if "action" in msg:
            if msg["action"] == "probe":
                router.route(Probe())
        elif "response" in msg:
            router.route(Response(HTTPStatus(msg["response"]), msg["message"]))
