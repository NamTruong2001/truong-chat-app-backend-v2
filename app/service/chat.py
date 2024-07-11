from beanie import PydanticObjectId
from fastapi import HTTPException

from exceptions import MessageSentError, MessageNotFound
from model.schemas import (
    UserMessageRequest,
    GetConversationMessagesWithPage,
    UserRead,
    UserReadMessage,
)
from service import ConversationService
from model.mongo import Message, UserMessage, ReadStatus


class MessageService:
    def __init__(self, conversation_service: ConversationService):
        self.conversation_service = conversation_service

    async def save_message(self, message: UserMessageRequest):
        is_in = await self.conversation_service.is_user_in_conversation_with_cache(
            user_id=message.sender_id, conversation_id=message.conversation_id
        )
        if not is_in:
            raise MessageSentError(
                message="Conversation not found",
                conversation={"id": message.conversation_id},
            )
        saved_message = UserMessage(
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
        is_in = await self.conversation_service.is_user_in_conversation_with_cache(
            user_id=str(current_user.id), conversation_id=request.conversation_id
        )
        if not is_in:
            raise HTTPException(detail="Conversation not found", status_code=400)

        messages = (
            await Message.find(
                Message.conversation_id == PydanticObjectId(request.conversation_id),
                with_children=True,
            )
            .sort(-Message.created_at)
            .skip((request.page - 1) * request.page_size)
            .limit(request.page_size)
            .to_list()
        )

        return messages

    # async def update_message_read_status(self, user_read_event: UserReadMessage):
    #     message = await Message.get(user_read_event.message_id, with_children=True)
    #     if not message:
    #         raise MessageNotFound(message_id=user_read_event.message_id)
    #
    #     cache_conversation = await self.conversation_service.get_cache_conversation(
    #         user_read_event.conversation_id
    #     )
    #
    #     if cache_conversation.type == "group":
    #         raise MessageSentError(
    #             message="Group conversation does not support read message",
    #             conversation=cache_conversation.dict(),
    #         )
    #
    #     if user_read_event.user_id not in cache_conversation.participants:
    #         raise MessageSentError(
    #             message="User is not in conversation",
    #             conversation=cache_conversation.dict(),
    #         )
    #
    #     message_read_by_user_ids = [str(read.user_id) for read in message.read_by]
    #     if user_read_event.user_id in message_read_by_user_ids:
    #         raise MessageSentError(
    #             message="Already read this message",
    #             conversation=cache_conversation.dict(),
    #         )
    #
    #     message.read_by.append(
    #         ReadStatus(
    #             user_id=PydanticObjectId(user_read_event.user_id),
    #         )
    #     )
    #     await message.save()
