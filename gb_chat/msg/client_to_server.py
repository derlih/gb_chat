from dataclasses import dataclass
from typing import Optional, Union

from .status import Status


@dataclass(frozen=True)
class Authenticate:
    login: str
    password: str


@dataclass
class Quit:
    pass


@dataclass(frozen=True)
class Presence:
    status: Optional[Status] = None


@dataclass(frozen=True)
class ChatFromClient:
    to: str
    message: str


@dataclass(frozen=True)
class Join:
    room: str


@dataclass(frozen=True)
class Leave:
    room: str


ClientToServerMessage = Union[Authenticate, Quit, Presence, ChatFromClient, Join, Leave]
