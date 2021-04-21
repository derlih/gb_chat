import errno
import selectors
import socket
from typing import Dict

import click

from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.message_splitter import MessageSplitter
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer
from gb_chat.server.server import Server


class NothingToRead(Exception):
    pass


class UnableToWrite(Exception):
    pass


class ClientConnection:
    def __init__(self, send_buffer: SendBuffer, msg_splitter: MessageSplitter) -> None:
        self._send_buffer = send_buffer
        self._msg_splitter = msg_splitter
        msg_framer = MessageFramer(send_buffer)
        serializer = Serializer(msg_framer)
        self._msg_sender = MessageSender(serializer)

    def read(self, sock: socket.socket) -> None:
        try:
            while True:
                self._msg_splitter.feed(sock.recv(1024))
        except socket.error as e:
            err = e.args[0]
            if err in (errno.EAGAIN, errno.EWOULDBLOCK):
                return

            raise NothingToRead() from e
        except Exception as e:
            raise NothingToRead() from e

    def write(self, sock: socket.socket) -> None:
        if not self._send_buffer.data:
            return

        size = sock.send(self._send_buffer.data)
        if size == 0:
            raise UnableToWrite()

        self._send_buffer.bytes_sent(size)

    @property
    def msg_sender(self) -> MessageSender:
        return self._msg_sender


class SocketHandler:
    def __init__(self, sel: selectors.BaseSelector, server: Server) -> None:
        self._sel = sel
        self._server = server
        self._clients: Dict[socket.socket, ClientConnection] = {}

    def accept_new_connection(self, sock: socket.socket) -> None:
        sock.setblocking(False)

        send_buffer = SendBuffer()
        msg_framer = MessageFramer(send_buffer)
        serializer = Serializer(msg_framer)
        msg_sender = MessageSender(serializer)

        parsed_msg_handler = ParsedMessageHandler(msg_router)
        deserializer = Deserializer(parsed_msg_handler)
        msg_splitter = MessageSplitter(deserializer)

        self._clients[sock] = ClientConnection(send_buffer, msg_splitter)
        self._server.on_client_connected(msg_sender)

        self._sel.register(
            sock, selectors.EVENT_READ | selectors.EVENT_WRITE, self._process_sock_event
        )

    def run(self) -> None:
        while True:
            events = self._sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def _disconnect(self, sock: socket.socket) -> None:
        self._sel.unregister(sock)
        sock.close()
        self._server.on_client_disconnected(self._clients[sock].msg_sender)
        del self._clients[sock]

    def _process_sock_event(self, sock: socket.socket, mask: int) -> None:
        try:
            connection = self._clients[sock]
            if mask & selectors.EVENT_READ:
                connection.read(sock)
            if mask & selectors.EVENT_WRITE:
                connection.write(sock)
        except Exception:
            self._disconnect(sock)


@click.command()
@click.option("-a", "--address", type=str, default="localhost")
@click.option("-p", "--port", type=click.IntRange(1, 65535), default=7777)
def main(address: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.setblocking(False)
        server_sock.bind((address, port))
        server_sock.listen()

        with selectors.DefaultSelector() as sel:
            server = Server()
            handler = SocketHandler(sel, server)

            sel.register(
                server_sock,
                selectors.EVENT_READ,
                lambda sock, _: handler.accept_new_connection(sock),  # type: ignore
            )

            handler.run()


if __name__ == "__main__":
    main()
