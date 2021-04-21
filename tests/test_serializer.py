from unittest.mock import MagicMock

import pytest
from gb_chat.io.exceptions import SerializationError
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer


@pytest.fixture
def send_buffer():
    return MagicMock(spec_set=SendBuffer)


@pytest.fixture
def sut(send_buffer):
    return Serializer(send_buffer)


def test_raises_when_encode_error(send_buffer):
    encode = MagicMock(side_effect=UnicodeError())
    sut = Serializer(send_buffer, encode=encode)
    with pytest.raises(SerializationError):
        sut.serialize({"a": "b"})


@pytest.mark.parametrize("exc", [TypeError(), OverflowError(), ValueError()])
def test_raises_when_json_error(exc):
    dumps = MagicMock(side_effect=exc)
    sut = Serializer(send_buffer, dumps=dumps)
    with pytest.raises(SerializationError):
        sut.serialize({"a": "b"})


def test_call_send_when_msg_serialized(sut, send_buffer):
    sut.serialize({"a": "b"})
    send_buffer.send.assert_called_once_with(b'{"a": "b"}')
