from typing import Any, Callable, Dict

from ..common.exceptions import InvalidRoomName
from ..common.room_name_validator import RoomNameValidator
from ..log import get_logger
from .chat_room import ChatRoom
from .client import Client

_logger: Any = get_logger()

ChatRoomFactory = Callable[[], ChatRoom]


class ChatRoomManager:
    def __init__(
        self,
        room_name_validator: RoomNameValidator,
        chat_room_factory: ChatRoomFactory = ChatRoom,
    ) -> None:
        self._room_name_validator = room_name_validator
        self._chat_room_factory = chat_room_factory
        self._rooms: Dict[str, ChatRoom] = {}

    def join(self, room_name: str, client: Client):
        if not self._room_name_validator.is_valid(room_name):
            raise InvalidRoomName(f"{room_name} is not valid")

        if room_name in self._rooms:
            room = self._rooms[room_name]
        else:
            _logger.debug("Room created", room=room_name)
            room = self._chat_room_factory()
            self._rooms[room_name] = room

        _logger.info("User joins group", room=room_name, client=client.name)
        room.join(client)

    def leave(self, room_name: str, client: Client, log_user_leave: bool = True):
        if room_name not in self._rooms:
            return

        room = self._rooms[room_name]
        if log_user_leave:
            _logger.info("User leaves group", room=room_name, client=client.name)
        room.leave(client)

        if room.empty:
            _logger.info("Remove empty group", room=room_name)
            del self._rooms[room_name]

    def leave_all(self, client: Client) -> None:
        for room_name in [*self._rooms.keys()]:
            self.leave(room_name, client, False)
