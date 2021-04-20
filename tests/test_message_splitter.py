from unittest.mock import MagicMock

import pytest
from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_splitter import MessageSizeError, MessageSplitter
from gb_chat.io.settings import HEADER_BYTEORDER, HEADER_SIZE


@pytest.fixture
def deserializer():
    return MagicMock(spec_set=Deserializer)


@pytest.fixture
def sut(deserializer):
    return MessageSplitter(deserializer)


def test_zero_msg_size_raises(sut):
    with pytest.raises(MessageSizeError):
        sut.feed(b"\0" * HEADER_SIZE)


@pytest.mark.parametrize(
    "data", [int(10).to_bytes(HEADER_SIZE, HEADER_BYTEORDER) + b"abc", b"\0\1"]
)
def test_no_call_deserializer_when_not_enought_data(data, sut, deserializer):
    sut.feed(data)
    assert not deserializer.on_msg.called


def prepare_msg(data: bytes):
    header = len(data).to_bytes(HEADER_SIZE, HEADER_BYTEORDER)
    return header + data


def test_call_deserializer_when_one_msg_feed(sut, deserializer):
    data = prepare_msg(b"abc")
    sut.feed(data)
    deserializer.on_msg.assert_called_once_with(b"abc")
