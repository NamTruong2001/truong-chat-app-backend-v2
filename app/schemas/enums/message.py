from enum import Enum


class UserMessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"


class SystemMessageType(str, Enum):
    SYSTEM_TEXT = "system_text"
