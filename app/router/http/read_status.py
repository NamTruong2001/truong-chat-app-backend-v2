from typing import Annotated

from fastapi import APIRouter, Depends, Query

from model.schemas import UserRead
from service import ReadStatusService
from util import validate_token


class ReadStatusRouter(APIRouter):
    def __init__(self, read_status_service: ReadStatusService, prefix: str):
        super().__init__(prefix=prefix)
        self.read_status_service = read_status_service
        self.add_api_route(
            "",
            self.read_latest_message_in_conversation,
            methods=["POST"],
        )

    async def read_latest_message_in_conversation(
        self,
        conversation_id: Annotated[str, Query],
        current_user: UserRead = Depends(validate_token),
    ):
        print(conversation_id, "conversation_id")
        res = await self.read_status_service.mark_latest_message_as_read(
            conversation_id=conversation_id, current_user=current_user
        )
        return res
