from json import JSONDecodeError, loads
from typing import Callable

from .exceptions import DeserializationError
from .parsed_msg_handler import JSON, ParsedMessageHandler
from .settings import MSG_ENCODING

Decode = Callable[[bytes], str]
Loads = Callable[[str], JSON]


class Deserializer:
    def __init__(
        self,
        handler: ParsedMessageHandler,
        decode: Decode = lambda x: x.decode(MSG_ENCODING),
        loads: Loads = loads,
    ) -> None:
        self._handler = handler
        self._decode = decode
        self._loads = loads

    def deserialize(self, msg: bytes) -> None:
        try:
            msg_str = self._decode(msg)
            msg_dict = self._loads(msg_str)
        except (UnicodeError, JSONDecodeError) as e:
            raise DeserializationError() from e

        self._handler.process(msg_dict)
