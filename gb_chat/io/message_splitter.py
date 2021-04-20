from .settings import BYTEORDER, HEADER_SIZE


class MessageSizeError(ValueError):
    pass


class MessageSplitter:
    def __init__(self, deserializer) -> None:
        self._deserializer = deserializer

    def feed(self, data: bytes) -> None:
        header = data[:HEADER_SIZE]
        msg_size = int.from_bytes(header, BYTEORDER)
        if msg_size == 0:
            raise MessageSizeError("Message size is 0")
