from json import dumps
from typing import Callable

from gb_chat.io.exceptions import SerializationError

from .json import JSON
from .send_buffer import SendBuffer
from .settings import MSG_ENCODING

Encode = Callable[[str], bytes]
Dumps = Callable[[JSON], str]


class Serializer:
    def __init__(
        self,
        send_buffer: SendBuffer,
        dumps: Dumps = dumps,
        encode: Encode = lambda x: x.encode(MSG_ENCODING),
    ) -> None:
        self._send_buffer = send_buffer
        self._dumps = dumps
        self._encode = encode

    def serialize(self, msg: JSON) -> None:
        try:
            msg_str = self._dumps(msg)
            msg_bytes = self._encode(msg_str)
        except (UnicodeError, TypeError, OverflowError, ValueError) as e:
            raise SerializationError() from e

        self._send_buffer.send(msg_bytes)
