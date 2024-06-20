from datetime import datetime
from typing import List, Union

from pydantic import BaseModel

from model.mongo import Conversation, Message
from schemas import UserRead
from schemas.enums import ConversationEnum


class ParticipantUser(BaseModel):
    joined_at: datetime
    user: UserRead


class ConversationResponse(Conversation):
    participants: List[ParticipantUser]
    latest_message: Union[List[Message], None] = None

    class Config:
        from_attributes = True


class RemoveParticipantsRequest(BaseModel):
    remove_participant_ids: List[str]
    conversation_id: str

    class Config:
        from_attributes = True


class AddParticipantsRequest(BaseModel):
    add_participant_ids: List[str]
    conversation_id: str

    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    title: str
    conversation_type: ConversationEnum
    participant_ids: List[str]

    class Config:
        from_attributes = True
