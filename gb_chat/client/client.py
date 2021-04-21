from ..msg.server_to_client import Probe, Response


class Client:
    def on_response(self, msg: Response) -> None:
        pass

    def on_probe(self, msg: Probe) -> None:
        pass
