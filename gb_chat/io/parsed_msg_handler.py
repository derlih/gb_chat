from typing import Any, Dict

JSON = Dict[str, Any]


class ParsedMessageHandler:
    def process(self, msg: JSON) -> None:
        pass
