from datetime import datetime
from typing import Union

# from .enums import UserMessageType
from pydantic import BaseModel, Field

from model.mongo import Attachment
from schemas.enums import UserMessageType
from schemas.enums.message import SystemMessageType


# class MessageType(str, Enum):
#     TEXT = "text"
#     IMAGE = "image"
#     VIDEO = "video"
#     FILE = "file"


class UserMessageRequest(BaseModel):
    conversation_id: str
    sender_id: str
    type: UserMessageType
    content: str
    attachment: Union[None, Attachment] = None

    class Config:
        use_enum_value = True


class SystemMessageRequest(BaseModel):
    conversation_id: str
    type: SystemMessageType
    attachment: Union[None, Attachment] = None

    class Config:
        use_enum_value = True


class MessageInResponse(UserMessageRequest):
    id: str
    created_at: datetime


class SystemMessageInResponse(SystemMessageRequest):
    id: str
    created_at: datetime
    system_content: dict


class GetConversationMessagesWithPage(BaseModel):
    conversation_id: str
    page: int = Field(gt=0, default=1)
    page_size: int = Field(gt=0, default=30)
