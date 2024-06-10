from typing import Annotated

from fastapi import APIRouter, Query, Depends

from service import ConversationService
from util.jwt import validate_token


class ConversationRouter:
    def __init__(self, conversation_service: ConversationService):
        self.router = APIRouter()
        self.conversation_service = conversation_service
        self.router.add_api_route("/all", self.get_conversations, methods=["GET"])
        self.router.add_api_route("/", self.get_conversation, methods=["GET"])
        self.router.add_api_route("/", self.create_conversation, methods=["POST"])
        self.router.add_api_route("/test", self.test, methods=["GET"])

    async def get_conversations(self, user_id: Annotated[str, Query()]):
        conversations = await self.conversation_service.get_user_conversation_sort_by_latest_message(
            user_id=user_id
        )
        return conversations

    async def get_conversation(
        self, conversation_id: Annotated[str, Query()], user_id: Annotated[str, Query()]
    ):
        conversation = await self.conversation_service.get_conversation_by_user_and_conversation_id(
            user_id=user_id, conversation_id=conversation_id
        )
        return conversation

    def create_conversation(self):
        pass

    async def remove_participant(
        self, conversation_id: Annotated[str, Query()], user_id: Annotated[str, Query()]
    ):
        conversation = await self.conversation_service.remove_participant(
            conversation_id=conversation_id, user_id=user_id
        )
        return conversation

    async def add_participant(
        self, conversation_id: Annotated[str, Query()], user_id: Annotated[str, Query()]
    ):
        conversation = await self.conversation_service.add_participant(
            conversation_id=conversation_id, user_id=user_id
        )
        return conversation

    def test(self, user: Annotated[str, Query] = Depends(validate_token)):
        print(user)
        return "test"

    def get_router(self):
        return self.router
