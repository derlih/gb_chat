from .settings import HEADER_BYTEORDER, HEADER_SIZE


class MessageSizeError(ValueError):
    pass


class MessageSplitter:
    def __init__(self, deserializer) -> None:
        self._deserializer = deserializer

    def feed(self, data: bytes) -> None:
        header = data[:HEADER_SIZE]
        rest_data = data[HEADER_SIZE:]
        msg_size = int.from_bytes(header, HEADER_BYTEORDER)
        if msg_size == 0:
            raise MessageSizeError("Message size is 0")

        if len(rest_data) < msg_size:
            return
