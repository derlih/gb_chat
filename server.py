import errno
import selectors
import socket
from typing import Dict, List

import click

from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.message_splitter import MessageSplitter
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer
from gb_chat.server.client import Client
from gb_chat.server.disconnector import Disconnector
from gb_chat.server.message_router import MessageRouter
from gb_chat.server.server import Server


class NothingToRead(Exception):
    pass


class UnableToWrite(Exception):
    pass


class ClientConnection:
    def __init__(
        self,
        sock: socket.socket,
        send_buffer: SendBuffer,
        msg_splitter: MessageSplitter,
        client: Client,
    ) -> None:
        self._sock = sock
        self._send_buffer = send_buffer
        self._msg_splitter = msg_splitter
        self._client = client

    def read(self) -> None:

        try:
            while True:
                data = self._sock.recv(1024)
                if not self._client.disconnector.should_disconnect:
                    self._msg_splitter.feed(data)
        except socket.error as e:
            err = e.args[0]
            if err in (errno.EAGAIN, errno.EWOULDBLOCK):
                return

            raise NothingToRead() from e
        except Exception as e:
            raise NothingToRead() from e

    def write(self) -> None:
        if not self._send_buffer.data:
            return

        size = self._sock.send(self._send_buffer.data)
        if size == 0:
            raise UnableToWrite()

        self._send_buffer.bytes_sent(size)

    @property
    def client(self) -> Client:
        return self._client

    @property
    def have_outgoing_data(self) -> bool:
        return bool(self._send_buffer.data)

    @property
    def socket(self) -> socket.socket:
        return self._sock


class SocketHandler:
    def __init__(self, sel: selectors.BaseSelector, server: Server) -> None:
        self._sel = sel
        self._server = server
        self._clients: Dict[socket.socket, ClientConnection] = {}

    def accept_new_connection(self, sock: socket.socket) -> None:
        sock.setblocking(False)

        disconnector = Disconnector()
        send_buffer = SendBuffer()
        msg_framer = MessageFramer(send_buffer)
        serializer = Serializer(msg_framer)
        msg_sender = MessageSender(serializer)
        client = Client(msg_sender, disconnector)
        msg_router = MessageRouter(self._server, client)
        parsed_msg_handler = ParsedMessageHandler(msg_router)
        deserializer = Deserializer(parsed_msg_handler)
        msg_splitter = MessageSplitter(deserializer)

        self._clients[sock] = ClientConnection(sock, send_buffer, msg_splitter, client)
        self._server.on_client_connected(client)

        self._sel.register(
            sock, selectors.EVENT_READ | selectors.EVENT_WRITE, self._process_sock_event  # type: ignore
        )

    def run(self) -> None:
        while True:
            self._process_io_events()
            self._disconnect_requested_clients()

    def _process_io_events(self) -> None:
        events = self._sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)

    def _disconnect_requested_clients(self) -> None:
        clients_to_disconnect: List[ClientConnection] = []
        for _, client_connection in self._clients.items():
            if (
                client_connection.client.disconnector.should_disconnect
                and not client_connection.have_outgoing_data
            ):
                clients_to_disconnect.append(client_connection)
        for client_connection in clients_to_disconnect:
            self._disconnect(client_connection.socket)

    def _disconnect(self, sock: socket.socket) -> None:
        self._sel.unregister(sock)
        sock.close()
        self._server.on_client_disconnected(self._clients[sock].client)
        del self._clients[sock]

    def _process_sock_event(self, sock: socket.socket, mask: int) -> None:
        try:
            connection = self._clients[sock]
            if mask & selectors.EVENT_READ:
                connection.read()
            if mask & selectors.EVENT_WRITE:
                connection.write()
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
