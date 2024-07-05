from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from model.mongo import ReadStatus, Message
from model.schemas import UserRead, UserReadMessage
from repository import ConversationRepository
from service import ConversationService
from socketio import AsyncServer


class ReadStatusService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        sio: AsyncServer,
        conversation_service: ConversationService,
    ):
        self.conversation_repository = conversation_repository
        self.conversation_service = conversation_service
        self._sio = sio

    def _map_to_dto(self, read_status: ReadStatus):

        read_event = UserReadMessage(
            user_id=read_status.user_id,
            conversation_id=read_status.conversation_id,
            message_id=read_status.latest_read_message_id,
        )
        return read_event

    async def mark_latest_message_as_read(
        self, conversation_id: str, current_user: UserRead
    ):
        is_in = await self.conversation_service.is_user_in_conversation_with_cache(
            user_id=str(current_user.id), conversation_id=conversation_id
        )
        if not is_in:
            raise HTTPException(
                detail={
                    "message": "User not in this conversation",
                    "conversation_id": conversation_id,
                },
                status_code=400,
            )
        read_status = await ReadStatus.find(
            ReadStatus.conversation_id == PydanticObjectId(conversation_id),
            ReadStatus.user_id == current_user.id,
        ).first_or_none()
        print(current_user, "current_user")
        print(read_status, "read_status")

        latest_message = (
            await Message.find({"conversation_id": PydanticObjectId(conversation_id)})
            .sort(-Message.created_at)
            .skip(0)
            .limit(1)
            .first_or_none()
        )
        print(latest_message, "latest_message")
        now_dt = datetime.now()
        if read_status is None:
            new_read_status = ReadStatus(
                latest_read_message_id=latest_message.id,
                read_at=now_dt,
                user_id=current_user.id,
                conversation_id=PydanticObjectId(conversation_id),
            )
            read_status = await new_read_status.insert()
        else:
            read_status.read_at = now_dt
            read_status.latest_read_message_id = latest_message.id
            read_status = await read_status.save()

        if read_status:
            read_event = self._map_to_dto(read_status)
            await self._sio.emit(
                "readMessage",
                jsonable_encoder(read_event.model_dump()),
                room=conversation_id,
            )

        return read_status
