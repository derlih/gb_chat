from gb_chat.io.exceptions import MessageTooBig

from .send_buffer import SendBuffer
from .settings import HEADER_BYTEORDER, HEADER_SIZE


class MessageFramer:
    def __init__(self, send_buffer: SendBuffer) -> None:
        self._send_buffer = send_buffer

    def frame(self, data: bytes) -> None:
        try:
            header_data = len(data).to_bytes(HEADER_SIZE, HEADER_BYTEORDER)
        except OverflowError:
            raise MessageTooBig(f"msg size is {len(data)} max={0xFF ** HEADER_SIZE}")
        self._send_buffer.send(header_data + data)
