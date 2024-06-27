from typing import Annotated

from fastapi import APIRouter, Query, Depends

from service import ConversationService
from util.jwt import validate_token
from model.schemas import (
    RemoveParticipantsRequest,
    AddParticipantsRequest,
    CreateConversationRequest,
)
from model.schemas.user import UserRead


class ConversationRouter(APIRouter):
    def __init__(self, conversation_service: ConversationService, prefix: str):
        super().__init__(prefix=prefix)
        self.conversation_service = conversation_service
        super().add_api_route("/all", self.get_conversations, methods=["GET"])
        super().add_api_route("", self.get_conversation, methods=["GET"])
        super().add_api_route("", self.create_conversation, methods=["POST"])
        super().add_api_route(
            "/remove-participant", self.remove_participant, methods=["POST"]
        )
        super().add_api_route(
            "/add-participant", self.add_participant, methods=["POST"]
        )
        # super().add_api_route("/leave", self.leave_conversation, methods=["POST"])
        super().add_api_route("/test", self.test, methods=["GET"])
        super().add_api_route(
            "/find-private-conversation",
            self.find_private_conversation_with_user,
            methods=["GET"],
        )

    async def get_conversations(self, user: UserRead = Depends(validate_token)):
        conversations = await self.conversation_service.get_user_conversation_sort_by_latest_message(
            user=user
        )
        return conversations

    async def get_conversation(
        self,
        conversation_id: Annotated[str, Query()],
        user: UserRead = Depends(validate_token),
    ):
        conversation = await self.conversation_service.get_conversation_by_user_and_conversation_id(
            user_id=str(user.id), conversation_id=conversation_id
        )
        return conversation

    async def create_conversation(
        self,
        create_conversation_request: CreateConversationRequest,
        user: UserRead = Depends(validate_token),
    ):
        conversation = await self.conversation_service.create_conversation(
            title=create_conversation_request.title,
            creator_id=str(user.id),
            conversation_type=create_conversation_request.conversation_type,
            participant_ids=create_conversation_request.participant_ids,
        )
        return conversation

    async def remove_participant(
        self,
        remove_participant_request: RemoveParticipantsRequest,
        user: UserRead = Depends(validate_token),
    ):
        conversation = await self.conversation_service.remove_participant(
            conversation_id=remove_participant_request.conversation_id,
            remove_user_ids=remove_participant_request.remove_participant_ids,
            current_user=user,
        )
        return conversation

    async def add_participant(
        self,
        add_participant_request: AddParticipantsRequest,
        user: UserRead = Depends(validate_token),
    ):
        conversation = await self.conversation_service.add_participant(
            conversation_id=add_participant_request.conversation_id,
            add_user_ids=add_participant_request.add_participant_ids,
            current_user=user,
        )
        return conversation

    # async def leave_conversation(
    #     self,
    #     conversation_id: Annotated[str, Query],
    #     user: UserRead = Depends(validate_token),
    # ):
    #     conversation = await self.conversation_service.leave_conversation(
    #         conversation_id=conversation_id, user=user
    #     )
    #     return conversation

    async def find_private_conversation_with_user(
        self,
        user_id: Annotated[str, Query],
        current_user: UserRead = Depends(validate_token),
    ):
        conversation = (
            await self.conversation_service.get_private_conversation_by_another_user_id(
                user_id=user_id, current_user=current_user
            )
        )
        return conversation

    def test(self, user: UserRead = Depends(validate_token)):
        print(user)
        return "test"
