from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"


class MessageRequest(BaseModel):
    conversation_id: str
    sender_id: str
    type: MessageType
    content: str

    class Config:
        use_enum_value = True


class MessageInResponse(MessageRequest):
    id: str
    created_at: datetime
    # updated_at: str
    # class Config:
    #     orm_mode = True
