from ..io.message_sender import MessageSender
from ..msg.server_to_client import Probe, Response


class Client:
    def __init__(self, msg_sender: MessageSender) -> None:
        self._msg_sender = msg_sender

    def on_response(self, msg: Response) -> None:
        pass

    def on_probe(self, msg: Probe) -> None:
        pass
