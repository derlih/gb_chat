from unittest.mock import MagicMock

import pytest
from gb_chat.io.message_splitter import MessageSizeError, MessageSplitter
from gb_chat.io.settings import HEADER_SIZE


@pytest.fixture
def deserializer():
    return MagicMock()


@pytest.fixture
def sut(deserializer):
    return MessageSplitter(deserializer)


def test_zero_msg_size_raises(sut):
    with pytest.raises(MessageSizeError):
        sut.feed(b"\0" * HEADER_SIZE)
