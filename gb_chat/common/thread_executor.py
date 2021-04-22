from queue import Empty, SimpleQueue
from typing import Any, Callable

from ..log import get_logger

Function = Callable[[], None]


class IoThreadExecutor:
    def __init__(self) -> None:
        self._queue: SimpleQueue[Function] = SimpleQueue()
        self._logger: Any = get_logger("IoThreadExecutor")

    def schedule(self, fun: Function) -> None:
        self._queue.put(fun)
        self._logger.debug("Schedule task", qsize=self._queue.qsize())

    def execute_all(self) -> None:
        try:
            while True:
                fun = self._queue.get_nowait()
                self._logger.debug("Execute task", qsize=self._queue.qsize())
                fun()
        except Empty:
            return
