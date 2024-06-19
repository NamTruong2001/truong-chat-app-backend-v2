from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel, Field

from model.mongo import Attachment


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
    attachment: Union[None, Attachment] = None

    class Config:
        use_enum_value = True


class MessageInResponse(MessageRequest):
    id: str
    created_at: datetime
    # updated_at: str
    # class Config:
    #     orm_mode = True


class GetConversationMessagesWithPage(BaseModel):
    conversation_id: str
    page: int = Field(gt=0, default=1)
    page_size: int = Field(gt=0, default=30)
