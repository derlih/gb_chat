from time import time
from typing import Callable, Union

from ..msg.client_to_server import Authenticate
from ..msg.client_to_server import Chat as ClientToServerChat
from ..msg.client_to_server import (ClientToServerMessage, Join, Leave,
                                    Presence, Quit)
from ..msg.server_to_client import Probe, Response, ServerToClientMessage
from .json import JSON
from .serializer import Serializer

TimeFactory = Callable[[], float]
Message = Union[ClientToServerMessage, ServerToClientMessage]


class MessageSender:
    def __init__(
        self, serializer: Serializer, time_factory: TimeFactory = time
    ) -> None:
        self._serializer = serializer
        self._time_factory = time_factory

    def send(self, msg: Message) -> None:
        msg_dict = self._convert(msg)
        if not isinstance(msg, Quit):
            msg_dict["time"] = self._time_factory()
        self._serializer.serialize(msg_dict)

    @staticmethod
    def _convert(msg: Message) -> JSON:
        if isinstance(msg, Response):
            return {"response": msg.code, "message": msg.msg}
        elif isinstance(msg, Probe):
            return {"action": "probe"}
        elif isinstance(msg, Authenticate):
            return {
                "action": "authenticate",
                "user": {"account_name": msg.login, "password": msg.password,},
            }
        elif isinstance(msg, Quit):
            return {"action": "quit"}
        elif isinstance(msg, Presence):
            res = {"action": "presence"}
            if msg.status:
                res["status"] = msg.status.value
            return res
        elif isinstance(msg, ClientToServerChat):
            return {"action": "msg", "to": msg.to, "message": msg.message}
        elif isinstance(msg, Join):
            return {"action": "join", "room": msg.room}
        elif isinstance(msg, Leave):
            return {"action": "leave", "room": msg.room}
