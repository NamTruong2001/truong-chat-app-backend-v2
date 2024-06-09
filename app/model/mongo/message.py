from datetime import datetime
from typing import Optional

from beanie import Document, Link, PydanticObjectId
from bson import ObjectId
from pydantic import Field, BaseModel
from model.mongo.conversation import Conversation
from model.mongo.user import User


class Attachment(BaseModel):
    file_name: str
    original_file_name: str


class Message(Document):
    conversation_id: PydanticObjectId
    sender_id: PydanticObjectId
    type: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attachment: Optional[Attachment] = None

    class Settings:
        collection = "messages"
        indexes = ["conversation_id", "sender", "created_at"]
