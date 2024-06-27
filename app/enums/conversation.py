from enum import Enum


class ConversationEnum(str, Enum):
    PRIVATE = "private"
    GROUP = "group"
    ALL = "all"
