from .deserializer import Deserializer
from .settings import HEADER_BYTEORDER, HEADER_SIZE


class MessageSizeError(ValueError):
    pass


class MessageSplitter:
    def __init__(self, deserializer: Deserializer) -> None:
        self._deserializer = deserializer
        self._data = b""

    def feed(self, data: bytes) -> None:
        self._data += data
        self._process_data()

    def _process_data(self) -> None:
        if len(self._data) < HEADER_SIZE:
            return

        header = self._data[:HEADER_SIZE]
        msg_size = int.from_bytes(header, HEADER_BYTEORDER)
        if msg_size == 0:
            raise MessageSizeError("Message size is 0")

        rest_data = self._data[HEADER_SIZE:]
        if len(rest_data) < msg_size:
            return

        msg_data = rest_data[:msg_size]
        self._deserializer.deserialize(msg_data)
        self._data = rest_data[msg_size:]
        self._process_data()
