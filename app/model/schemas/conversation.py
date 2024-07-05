from datetime import datetime
from typing import List, Union

from pydantic import BaseModel, Field

from model.mongo import Conversation, Message, UserMessage, SystemMessage
from model.mongo.read_status import ReadStatus
from model.schemas import UserRead
from enums import ConversationEnum


class ParticipantUser(BaseModel):
    joined_at: datetime
    user: UserRead


class ConversationWithLatestMessageAndUser(Conversation):
    participants: List[ParticipantUser]
    latest_message: list[Union[SystemMessage, UserMessage, Message]] = Field(
        default_factory=list,
        discriminator="type",
    )
    read_statuses: list[ReadStatus] = Field(default_factory=list)

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


class CacheConversation(BaseModel):
    id: str
    title: str
    type: str
    creator_id: str
    created_at: str
    participants: List[str]
