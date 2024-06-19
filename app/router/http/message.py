from typing import Annotated

from fastapi import APIRouter, Depends
from schemas import GetConversationMessagesWithPage
from schemas import UserRead
from service import MessageService
from util import validate_token


class MessageRouter(APIRouter):
    def __init__(self, prefix: str, message_service: MessageService):
        super().__init__(prefix=prefix)
        self.message_service = message_service
        super().add_api_route("", self.get_messages_with_paginate, methods=["POST"])

    async def get_messages_with_paginate(
        self,
        request: GetConversationMessagesWithPage,
        user: UserRead = Depends(validate_token),
    ):
        return await self.message_service.get_messages_with_paginate(
            current_user=user, request=request
        )
