from dataclasses import dataclass

from ..io.message_sender import MessageSender
from .disconnector import Disconnector


@dataclass(frozen=True)
class Client:
    msg_sender: MessageSender
    disconnector: Disconnector
