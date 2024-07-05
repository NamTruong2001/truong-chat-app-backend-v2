from datetime import datetime

from beanie import Document, PydanticObjectId, Link
from model.mongo import User, Conversation


class ReadStatus(Document):
    latest_read_message_id: PydanticObjectId
    read_at: datetime
    user_id: PydanticObjectId
    conversation_id: PydanticObjectId

    class Settings:
        indexes = ["user_id", "conversation_id"]
