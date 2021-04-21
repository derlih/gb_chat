import select
import time
from socket import AF_INET, SOCK_STREAM, socket

import click

from gb_chat.client.client import Client
from gb_chat.client.message_router import MessageRouter
from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.message_splitter import MessageSplitter
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer


def read_data(sock: socket, msg_splitter: MessageSplitter) -> None:
    data = sock.recv(1024)
    msg_splitter.feed(data)


def write_data(sock: socket, send_buffer: SendBuffer) -> None:
    size = sock.send(send_buffer.data)
    send_buffer.bytes_sent(size)


def mainloop(
    sock: socket, send_buffer: SendBuffer, msg_splitter: MessageSplitter
) -> None:
    while True:
        r, w, _ = select.select([sock], [sock], [], 0)
        if r:
            read_data(sock, msg_splitter)
        if w:
            write_data(sock, send_buffer)

        time.sleep(0.01)


@click.command()
@click.option("-a", "--address", type=str, default="localhost")
@click.option("-p", "--port", type=click.IntRange(1, 65535), default=7777)
def main(address: str, port: int) -> None:
    send_buffer = SendBuffer()
    msg_framer = MessageFramer(send_buffer)
    serializer = Serializer(msg_framer)
    msg_sender = MessageSender(serializer)
    client = Client(msg_sender)
    msg_router = MessageRouter(client)
    parsed_msg_handler = ParsedMessageHandler(msg_router)
    deserializer = Deserializer(parsed_msg_handler)
    msg_splitter = MessageSplitter(deserializer)

    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setblocking(False)
        sock.connect((address, port))
        mainloop(sock, send_buffer, msg_splitter)


if __name__ == "__main__":
    main()
