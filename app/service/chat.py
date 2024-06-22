from beanie import PydanticObjectId

from exceptions import MessageSentError
from schemas import UserMessageRequest, GetConversationMessagesWithPage, UserRead
from service import ConversationService
from model.mongo import Message


class MessageService:
    def __init__(self, conversation_service: ConversationService):
        self.conversation_service = conversation_service
        pass

    async def save_message(self, message: UserMessageRequest):
        is_in = await self.conversation_service.is_user_in_conversation(
            user_id=message.sender_id, conversation_id=message.conversation_id
        )
        if not is_in:
            raise MessageSentError(message="Conversation not found", conversation={})
        saved_message = Message(
            sender_id=PydanticObjectId(message.sender_id),
            conversation_id=PydanticObjectId(message.conversation_id),
            content=message.content,
            type=message.type,
            attachment=message.attachment,
        )
        await saved_message.insert()
        return saved_message

    async def get_messages_with_paginate(
        self, current_user: UserRead, request: GetConversationMessagesWithPage
    ):
        is_in = await self.conversation_service.is_user_in_conversation(
            user_id=str(current_user.id), conversation_id=request.conversation_id
        )
        if not is_in:
            raise MessageSentError(message="Conversation not found", conversation={})

        messages = (
            await Message.find(
                Message.conversation_id == PydanticObjectId(request.conversation_id),
            )
            .sort(-Message.created_at)
            .skip((request.page - 1) * request.page_size)
            .limit(request.page_size)
            .to_list()
        )

        return messages
