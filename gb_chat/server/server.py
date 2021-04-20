from ..msg.client_to_server import (Authenticate, Chat, Join, Leave, Presence,
                                    Quit)


class Server:
    def on_auth(self, msg: Authenticate) -> None:
        pass

    def on_quit(self, msg: Quit) -> None:
        pass

    def on_presense(self, msg: Presence) -> None:
        pass

    def on_chat(self, msg: Chat) -> None:
        pass

    def on_join(self, msg: Join) -> None:
        pass

    def on_leave(self, msg: Leave) -> None:
        pass
