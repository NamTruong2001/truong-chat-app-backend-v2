from typing import List

from model.mongo import Conversation, Message


class ConversationWithLatestMessage(Conversation):
    latest_message: List[Message]

    class Config:
        from_attributes = True
