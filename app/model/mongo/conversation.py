from datetime import datetime
from beanie import Document, Link, PydanticObjectId
from typing import List, Union, Optional

from pydantic import Field, BaseModel
from .user import User


class Participant(BaseModel):
    user_id: PydanticObjectId
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(Document):
    title: str
    creator: Link[User]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    type: str
    participants: List[Participant] = []

    class Settings:
        collection = "conversation"
        indexes = ["creator, created_at"]

    async def remove_participant(self, user_id: str):
        self.participants = [
            participant
            for participant in self.participants
            if participant.user_id != user_id
        ]

    async def add_participant(self, user_id: str):
        self.participants.append(Participant(user_id=user_id))
