class Disconnector:
    def __init__(self) -> None:
        self._flag = False

    def disconnect(self) -> None:
        self._flag = True

    @property
    def should_disconnect(self) -> bool:
        return self._flag
