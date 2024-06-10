from datetime import datetime
from beanie import Document, Link, PydanticObjectId
from typing import List, Union, Optional

from pydantic import Field, BaseModel
from .user import User
from exceptions import ParticipantAlreadyExists


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
        new_participants = [
            participant
            for participant in self.participants
            if participant.user_id != user_id
        ]
        if len(new_participants) == len(self.participants):
            raise ParticipantAlreadyExists("Participant does not exist")

        self.participants = new_participants

    async def add_participant(self, user_id: str):
        participants_user_ids = [
            participant.user_id for participant in self.participants
        ]
        if user_id in participants_user_ids:
            raise ParticipantAlreadyExists("Participant already exists")
        self.participants.append(Participant(user_id=user_id))

    async def test(self):
        pass
