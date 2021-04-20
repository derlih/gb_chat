from unittest.mock import MagicMock

import pytest
from gb_chat.io.message_splitter import MessageSizeError, MessageSplitter
from gb_chat.io.settings import HEADER_BYTEORDER, HEADER_SIZE


@pytest.fixture
def deserializer():
    return MagicMock()


@pytest.fixture
def sut(deserializer):
    return MessageSplitter(deserializer)


def test_zero_msg_size_raises(sut):
    with pytest.raises(MessageSizeError):
        sut.feed(b"\0" * HEADER_SIZE)


def test_no_call_deserializer_when_not_enought_data(sut, deserializer):
    header = int(10).to_bytes(HEADER_SIZE, HEADER_BYTEORDER)
    sut.feed(header + b"abc")
    assert not deserializer.on_msg.called
