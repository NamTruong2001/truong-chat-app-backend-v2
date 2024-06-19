import asyncio

import socketio.exceptions
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from socketio import AsyncNamespace

from exceptions import MessageSentError
from schemas import MessageRequest
from schemas.enums import ConversationEnum, SocketAction
from service.user import UserService
from util import validate_socket_connection
from service import ConversationService, MessageService


class ChatSocket(AsyncNamespace):
    def __init__(
        self,
        name_space: str,
        chat_service: MessageService,
        conversation_service: ConversationService,
        user_service: UserService,
    ):
        super().__init__(name_space)
        self.chat_service = chat_service
        self.conversation_service = conversation_service
        self.user_service = user_service

    async def on_connect(self, sid, auth, environment):
        print(sid, "connected")
        # print("Connected")
        user = validate_socket_connection(auth)
        await self.save_session(sid, {"user_id": str(user.id)})
        updated_user_connections = self.user_service.manage_user_socket_connection(
            user_id=str(user.id), socket_id=sid, connect_action=SocketAction.CONNECT
        )

        conversations = await self.conversation_service.get_user_conversations(
            user_id=str(user.id),
            conversation_type=ConversationEnum.PRIVATE,
            is_all=True,
        )

        online_status_private_chat_participants = []
        emit_presence_tasks = []
        for conversation in conversations:
            self.enter_room(sid=sid, room=f"{str(conversation.id)}")
            # only notify online status in private conversation
            if conversation.type == ConversationEnum.PRIVATE:
                str_conversation_id = str(conversation.id)
                if len(updated_user_connections) == 1:
                    emit_presence_tasks.append(
                        self.emit(
                            event="presence",
                            room=str_conversation_id,
                            skip_sid=sid,
                            data={
                                "conversation_id": str_conversation_id,
                                "user": str(user.id),
                                "is_online": True,
                            },
                        )
                    )
                # get the online status of participants in each user private conversations
                for participant in conversation.participants:
                    online_status = {
                        "user_id": str(participant.user_id),
                        "conversation_id": str(conversation.id),
                    }
                    if str(participant.user_id) != str(user.id):
                        if self.user_service.is_user_online(str(participant.user_id)):
                            online_status["online"] = True
                        else:
                            online_status["online"] = False
                        online_status_private_chat_participants.append(online_status)
        await asyncio.gather(*emit_presence_tasks)
        await self.emit(
            "presence", data=online_status_private_chat_participants, to=sid
        )

    async def on_disconnect(self, sid):
        user_session = await self.get_session(sid)
        user_id = user_session["user_id"]

        updated_user_connections = self.user_service.manage_user_socket_connection(
            user_id=str(user_id), socket_id=sid, connect_action=SocketAction.DISCONNECT
        )
        emit_presence_tasks = []
        if len(updated_user_connections) == 0:
            # conversations = await self.conversation_service.get_user_conversations(
            #     user_id=str(user_id),
            #     conversation_type=ConversationEnum.PRIVATE,
            #     is_all=True,
            # )
            for room in self.rooms(sid=sid):
                emit_presence_tasks.append(
                    self.emit(
                        event="presence",
                        room=room,
                        skip_sid=list(updated_user_connections),
                        data={
                            "conversation_id": room,
                            "user": str(user_id),
                            "is_online": False,
                        },
                    )
                )
        await asyncio.gather(*emit_presence_tasks)

    async def on_message(self, sid, data):
        try:
            user_session = await self.get_session(sid)
            message_request = MessageRequest(**data, sender_id=user_session["user_id"])
            saved_message = await self.chat_service.save_message(message_request)
            await self.emit(
                "message",
                data=jsonable_encoder(saved_message.model_dump()),
                room=message_request.conversation_id,
            )
        except ValidationError as ve:
            await self.emit(
                event="message",
                to=sid,
                data={
                    "error": {
                        "message": "Message validation error",
                        "details": ve.errors(),
                    }
                },
            )
        except MessageSentError as mse:
            await self.emit(
                event="message",
                to=sid,
                data={"error": {"message": mse.message, "details": {}}},
            )

    async def on_presence(self, sid, data):
        print(data)
