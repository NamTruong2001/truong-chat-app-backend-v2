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

    def remove_participant(self, user_ids: list[str]):
        removed_participants = []
        remaining_participants = []
        for participant in self.participants:
            if str(participant.user_id) in user_ids:
                removed_participants.append(participant)
            else:
                remaining_participants.append(participant)
        self.participants = remaining_participants
        return removed_participants, remaining_participants

    def add_participant(self, user_ids: list[str]):
        participants_user_ids = [
            str(participant.user_id) for participant in self.participants
        ]
        new_participants = [
            Participant(user_id=PydanticObjectId(user_id))
            for user_id in user_ids
            if user_id not in participants_user_ids
        ]
        # for user_id in user_ids:
        #     if user_id in participants_user_ids:
        #         raise ParticipantAlreadyExists("Participant already exists")
        print(new_participants)
        self.participants.extend(new_participants)
        return new_participants

    async def test(self):
        pass
