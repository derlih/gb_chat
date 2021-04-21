import errno
import select
import socket
from typing import Any

import click
import structlog

from gb_chat.client.client import Client
from gb_chat.client.message_router import MessageRouter
from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.message_splitter import MessageSplitter
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer
from gb_chat.log import configure_logging, get_logger

_logger: Any = get_logger()


class NothingToRead(Exception):
    pass


class UnableToWrite(Exception):
    pass


def read_data(sock: socket.socket, msg_splitter: MessageSplitter) -> None:
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                raise NothingToRead()
            msg_splitter.feed(data)
    except socket.error as e:
        err = e.args[0]
        if err in (errno.EAGAIN, errno.EWOULDBLOCK):
            return

        raise NothingToRead() from e


def write_data(sock: socket.socket, send_buffer: SendBuffer) -> None:
    if not send_buffer.data:
        return

    size = sock.send(send_buffer.data)
    if size == 0:
        raise UnableToWrite()

    send_buffer.bytes_sent(size)


def mainloop(
    sock: socket.socket, send_buffer: SendBuffer, msg_splitter: MessageSplitter
) -> None:
    while True:
        r, w, _ = select.select([sock], [sock], [], 0)
        if r:
            read_data(sock, msg_splitter)
        if w:
            write_data(sock, send_buffer)


@click.command()
@click.option("-a", "--address", type=str, default="localhost")
@click.option("-p", "--port", type=click.IntRange(1, 65535), default=7777)
def main(address: str, port: int) -> None:
    configure_logging(structlog.dev.ConsoleRenderer(colors=False))
    logger = _logger.bind(address=address, port=port)

    send_buffer = SendBuffer()
    msg_framer = MessageFramer(send_buffer)
    serializer = Serializer(msg_framer)
    msg_sender = MessageSender(serializer)
    client = Client(msg_sender)
    msg_router = MessageRouter(client)
    parsed_msg_handler = ParsedMessageHandler(msg_router)
    deserializer = Deserializer(parsed_msg_handler)
    msg_splitter = MessageSplitter(deserializer)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((address, port))
        except ConnectionRefusedError:
            logger.error("Server unavailable")
            return

        logger.info("Connected to server")
        sock.setblocking(False)

        try:
            mainloop(sock, send_buffer, msg_splitter)
        except (KeyboardInterrupt, NothingToRead, UnableToWrite):
            logger.info("Disconnected")
        except Exception:
            logger.exception("Disconnected")


if __name__ == "__main__":
    main()
