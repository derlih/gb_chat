from dataclasses import dataclass
from typing import Optional

from ..io.message_sender import MessageSender
from .disconnector import Disconnector


@dataclass
class Client:
    msg_sender: MessageSender
    disconnector: Disconnector

    name: Optional[str] = None
