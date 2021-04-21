class SendBuffer:
    def __init__(self) -> None:
        self._data = b""

    @property
    def data(self) -> bytes:
        return self._data

    def send(self, data: bytes) -> None:
        self._data += data

    def bytes_sent(self, size: int) -> None:
        if size > len(self._data):
            raise ValueError(
                f"Sent more than have size={size} len(self.data)={len(self._data)}"
            )

        self._data = self._data[size:]
