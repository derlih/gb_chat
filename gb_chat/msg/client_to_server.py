from dataclasses import dataclass
from typing import Optional, Union

from .status import Status


@dataclass(frozen=True)
class Authenticate:
    login: str
    password: str


class Quit:
    pass


@dataclass(frozen=True)
class Presence:
    status: Optional[Status]


@dataclass(frozen=True)
class Chat:
    to: str
    message: str


@dataclass(frozen=True)
class Join:
    room: str


@dataclass(frozen=True)
class Leave:
    room: str


ClientToServerMessage = Union[Authenticate, Quit, Presence, Chat, Join, Leave]
