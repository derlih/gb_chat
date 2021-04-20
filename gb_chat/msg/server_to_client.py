from dataclasses import dataclass
from http import HTTPStatus
from typing import Union


@dataclass(frozen=True)
class Response:
    code: HTTPStatus
    msg: str


class Probe:
    pass


ServerToClientMessage = Union[Response, Probe]
