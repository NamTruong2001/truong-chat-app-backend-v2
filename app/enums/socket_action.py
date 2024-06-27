from enum import Enum


class SocketAction(str, Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
