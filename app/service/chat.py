from model.mongo import Message
from schemas import MessageRequest


class ChatService:
    def __init__(self):
        pass

    async def save_message(self, message: MessageRequest):
        message_db = Message(
            sender_id=message.sender_id,
            conversation_id=message.conversation_id,
            message=message.message,
            message_type=message.message_type,
        )
        await message_db.insert()
