from typing import List

from pydantic import BaseModel

from model.mongo import Conversation, Message


class ConversationWithLatestMessage(Conversation):
    latest_message: List[Message]

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
    conversation_type: str = "group"
    participant_ids: List[str]

    class Config:
        from_attributes = True
