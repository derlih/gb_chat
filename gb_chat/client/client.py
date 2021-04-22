from typing import Any

from gb_chat.msg.status import Status

from ..io.message_sender import MessageSender
from ..log import get_logger
from ..msg.client_to_server import Authenticate, Chat, Join, Leave, Presence
from ..msg.server_to_client import Probe, Response

_logger: Any = get_logger()


class Client:
    def __init__(self, msg_sender: MessageSender) -> None:
        self._msg_sender = msg_sender
        self._logged_in = False

    def login(self, username: str, password: str) -> None:
        _logger.info("Send auth", username=username)
        self._msg_sender.send(Authenticate(username, password))

    def send_msg(self, to_user: str, msg: str) -> None:
        _logger.info("Send chat message", to=to_user, msg=msg)
        self._msg_sender.send(Chat(to_user, msg))

    def join_room(self, room: str) -> None:
        _logger.info("Join room", room=room)
        self._msg_sender.send(Join(room))

    def leave_room(self, room: str) -> None:
        _logger.info("Leave room", room=room)
        self._msg_sender.send(Leave(room))

    def on_response(self, msg: Response) -> None:
        if not self._logged_in:
            self._handle_auth_response(msg)

    def on_probe(self, msg: Probe) -> None:
        _logger.debug("Probe received")

    def _handle_auth_response(self, msg: Response) -> None:
        self._msg_sender.send(Presence(Status.ONLINE))
