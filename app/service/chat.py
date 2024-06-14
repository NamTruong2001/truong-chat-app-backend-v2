from beanie import PydanticObjectId

from model.mongo import Message
from schemas import MessageRequest


class ChatService:
    def __init__(self):
        pass

    async def save_message(self, message: MessageRequest):
        saved_message = Message(
            sender_id=PydanticObjectId(message.sender_id),
            conversation_id=PydanticObjectId(message.conversation_id),
            content=message.content,
            type=message.type,
            attachment=message.attachment,
        )
        await saved_message.insert()
        return saved_message
