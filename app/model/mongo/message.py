from datetime import datetime
from typing import Optional

from beanie import Document, Link, PydanticObjectId
from pydantic import Field, BaseModel
from schemas.enums import UserMessageType, SystemMessageType


class Attachment(BaseModel):
    file_name: str
    original_file_name: str


class Message(Document):
    conversation_id: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attachment: Optional[Attachment] = None

    class Settings:
        is_root = True
        collection = "messages"
        indexes = ["conversation_id", "sender_id", "created_at"]


class SystemMessage(Message):
    system_type: SystemMessageType
    system_content: dict


class UserMessage(Message):
    type: UserMessageType
    sender_id: PydanticObjectId
    content: str
