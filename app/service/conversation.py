import asyncio

from beanie import PydanticObjectId
from beanie.odm.operators.find.comparison import In
from bson import ObjectId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from socketio import AsyncServer
from util.global_variable import chat_namespace

from model.mongo import Conversation, Participant, User, Message, SystemMessage
from exceptions import (
    ConversationNotFound,
    UserNotFound,
    ParticipantAlreadyExists,
    ParticipantNotFound,
)
from repository import ConversationRepository, UserRepository
from model.schemas.conversation import ConversationWithLatestMessageAndUser
from enums import ConversationEnum, SystemMessageType
from model.schemas.user import UserRead
from util.aggregate_criteria import (
    conversation_participant_user_map,
    conversation_with_latest_message_map,
)


class ConversationService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        sio: AsyncServer,
        user_repository: UserRepository,
    ):
        self.conversation_repository = conversation_repository
        self.user_repository = user_repository
        self.sio = sio

    async def get_conversation_by_user_and_conversation_id(
        self, user_id: str, conversation_id: str
    ):
        conversation = await Conversation.find(
            {
                "$and": [
                    {"_id": ObjectId(conversation_id)},
                    {"participants": {"$elemMatch": {"user_id": ObjectId(user_id)}}},
                ]
            }
        ).first_or_none()
        if not conversation:
            raise ConversationNotFound(conversation_id=conversation_id)
        return conversation

    def _map_message_with_latest_message(
        self, messages: list[Message], conversations: list[Conversation]
    ):
        id_conversation = {
            conversation.id: ConversationWithLatestMessageAndUser(
                id=conversation.id,
                title=conversation.title,
                creator=conversation.creator,
                created_at=conversation.created_at,
                type=conversation.type,
                participants=[
                    *conversation.participants,
                ],
            )
            for conversation in conversations
        }
        for message in messages:
            id_conversation[message.conversation_id].latest_message.append(message)

        for key in id_conversation.keys():
            id_conversation[key].latest_message = sorted(
                id_conversation[key].latest_message,
                key=lambda x: x.created_at,
                reverse=True,
            )

        return list(id_conversation.values())

    async def get_user_conversation_sort_by_latest_message(self, user: UserRead):
        """
        :param user:
        :return:
         group message by conversation id and by max created_at
        filter conversation of that user and join with max created_at message by conversation_id
        """
        conversations = await Conversation.aggregate(
            [
                {"$match": {"participants.user_id": PydanticObjectId(user.id)}},
                *conversation_participant_user_map,
                *conversation_with_latest_message_map,
                {"$sort": {"latest_message.created_at": -1}},
            ],
            projection_model=ConversationWithLatestMessageAndUser,
        ).to_list()
        # the aggregate function doesn't support with_children=True, so it can't get children of the Message class
        # one more query to get children of the Message class
        latest_message_ids = [
            message.id
            for conversation in conversations
            for message in conversation.latest_message
        ]
        latest_messages = await Message.find(
            In(Message.id, latest_message_ids), with_children=True
        ).to_list()
        conversations_message = self._map_message_with_latest_message(
            messages=latest_messages, conversations=conversations
        )
        return conversations_message

    async def create_conversation(
        self,
        title: str,
        creator_id: str,
        conversation_type: str,
        participant_ids: list[str],
    ):
        creator = await User.find_one(User.id == PydanticObjectId(creator_id))
        if creator is None:
            raise UserNotFound(creator_id)
        participants = [
            Participant(user_id=PydanticObjectId(participant_id))
            for participant_id in participant_ids
        ]
        participants.append(Participant(user_id=PydanticObjectId(creator_id)))
        conversation = Conversation(
            title=title,
            creator=creator,
            type=conversation_type,
            participants=participants,
        )
        await conversation.insert()
        return conversation

    async def get_conversation_info(self, conversation_id: str):
        conversation = await Conversation.find_one({"_id": ObjectId(conversation_id)})
        if not conversation:
            raise ConversationNotFound(conversation_id)
        return conversation

    """
    test: 
        - check added user successfully also added socket id to socketio managed room | X
        - check added user receive message right after added | X
        - check if user receive added message type right on added | X
        - checked added multiple socket ids to room right on added | X
    """

    async def add_participant(
        self, conversation_id: str, add_user_ids: list[str], current_user: UserRead
    ):
        try:
            # add_user = await User.find_one(User.id == PydanticObjectId(add_user_id))
            # if add_user is None:
            #     raise UserNotFound(add_user_id)\
            """get the new users and the conversation from mongo"""
            new_users = await self.user_repository.get_many_users(
                [PydanticObjectId(user_id) for user_id in add_user_ids]
            )
            new_user_ids = [str(user.id) for user in new_users]
            conversation = await self.get_conversation_by_user_and_conversation_id(
                conversation_id=conversation_id, user_id=str(current_user.id)
            )

            """add new user ids to conversation of mongodb and redis"""
            added_participants = conversation.add_participant(new_user_ids)
            added_participant_user_ids = [
                str(added_participant.user_id)
                for added_participant in added_participants
            ]
            newly_added_users = [
                {"id": str(user.id), "username": user.username}
                for user in new_users
                if str(user.id) in added_participant_user_ids
            ]

            if not added_participants:
                raise ParticipantAlreadyExists("Participants already exist")
            await conversation.save()
            if self.conversation_repository.is_conversation_cached(conversation_id):
                self.conversation_repository.add_user_id_to_conversation(
                    conversation_id=conversation_id, user_id=added_participant_user_ids
                )
            """create system message"""
            system_message = SystemMessage(
                conversation_id=conversation.id,
                system_type=SystemMessageType.SYSTEM_NOTIFY,
                system_content={
                    "type": "add_participant",
                    "added_users": newly_added_users,
                    "initiator": {
                        "id": str(current_user.id),
                        "username": str(current_user.username),
                    },
                },
            )
            await system_message.insert()

            """add user to room managed by socketio and sent message to notify """
            for user_id in added_participant_user_ids:
                user_socket_ids = self.user_repository.get_user_sockets(str(user_id))
                for user_socket_id in user_socket_ids:
                    self.sio.enter_room(
                        room=conversation_id,
                        sid=user_socket_id,
                        namespace=chat_namespace,
                    )

            await self.sio.emit(
                namespace=chat_namespace,
                event="message",
                data=jsonable_encoder(system_message.model_dump()),
                room=conversation_id,
            )

            return conversation
        except ParticipantAlreadyExists as pae:
            raise HTTPException(status_code=400, detail=str(pae))
        except ConversationNotFound as cnf:
            raise HTTPException(status_code=400, detail=str(cnf))
        except UserNotFound as unf:
            raise HTTPException(status_code=400, detail=str(unf))

    # handle kick user socketio from conversation
    async def remove_participant(
        self, conversation_id: str, remove_user_ids: list[str], current_user: UserRead
    ):
        try:
            """get the removed users and the conversation from mongo"""

            db_users = await self.user_repository.get_many_users(
                [PydanticObjectId(user_id) for user_id in remove_user_ids]
            )
            user_ids_for_remove = [str(user.id) for user in db_users]
            conversation = await self.get_conversation_by_user_and_conversation_id(
                conversation_id=conversation_id, user_id=str(current_user.id)
            )

            removed_participants, remaining_participants = (
                conversation.remove_participant(user_ids_for_remove)
            )
            removed_participant_ids = [
                participant.user_id for participant in removed_participants
            ]
            removed_users = [
                {"id": str(removed_user.id), "username": removed_user.username}
                for removed_user in db_users
                if removed_user.id in removed_participant_ids
            ]

            """if one user is removed but its id equal to the id of the user making request -> leave
            else get removed or
            """
            if not removed_participants:
                raise ParticipantNotFound("Participants not found")
            await conversation.save()
            if self.conversation_repository.is_conversation_cached(conversation_id):
                self.conversation_repository.remove_user_id_from_conversation(
                    conversation_id=conversation_id, user_id=remove_user_ids
                )

            """create system message"""
            system_message = SystemMessage(
                conversation_id=conversation.id,
                system_type=SystemMessageType.SYSTEM_NOTIFY,
                system_content=(
                    {
                        "type": "leave_conversation",
                        "removed_users": removed_users,
                        "initiator": {
                            "id": str(current_user.id),
                            "username": str(current_user.username),
                        },
                    }
                    if (
                        len(removed_participants) == 1
                        and removed_participants[0].user_id == current_user.id
                    )
                    else {
                        "type": "remove_conversation",
                        "removed_users": removed_users,
                        "initiator": {
                            "id": str(current_user.id),
                            "username": str(current_user.username),
                        },
                    }
                ),
            )
            await system_message.insert()

            await self.sio.emit(
                namespace="/chat",
                event="message",
                data=jsonable_encoder(system_message.model_dump()),
                room=conversation_id,
            )

            """remove user from room managed by socketio"""
            for user_id in removed_participant_ids:
                for socket_id in self.user_repository.get_user_sockets(user_id):
                    # print(f"Room before update")
                    # for room in self.sio.rooms(sid=socket_id, namespace=chat_namespace):
                    #     print(room)
                    self.sio.leave_room(
                        sid=socket_id, room=conversation_id, namespace=chat_namespace
                    )
                    # print(f"Room after update")
                    # for room in self.sio.rooms(sid=socket_id, namespace=chat_namespace):
                    #     print(room)

            return conversation
        except ParticipantNotFound as pnf:
            raise HTTPException(status_code=400, detail=str(pnf))
        except ConversationNotFound as cnf:
            raise HTTPException(status_code=400, detail=str(cnf))
        except UserNotFound as unf:
            raise HTTPException(status_code=400, detail=str(unf))

    async def get_user_conversations(
        self, user_id: str, conversation_type: ConversationEnum
    ):
        if conversation_type is ConversationEnum.ALL:
            search_criteria = {"participants.user_id": PydanticObjectId(user_id)}
        else:
            search_criteria = {
                "$and": [
                    {"participants.user_id": PydanticObjectId(user_id)},
                    {"type": conversation_type.value},
                ]
            }

        conversations = await Conversation.find(search_criteria).to_list()
        return conversations

    async def leave_conversation(self, user: UserRead, conversation_id: str):
        try:
            is_in = self.is_user_in_conversation(
                user_id=str(user.id), conversation_id=conversation_id
            )
            if not is_in:
                raise ConversationNotFound("Conversation not found")
            conversation = await self.get_conversation_by_user_and_conversation_id(
                conversation_id=conversation_id, user_id=str(user.id)
            )
            removed_participants = conversation.remove_participant([str(user.id)])
            if not removed_participants:
                raise ParticipantNotFound("Participants not found")

            await conversation.save()
            return conversation
        except ParticipantNotFound as pnf:
            raise HTTPException(status_code=400, detail=str(pnf))
        except ConversationNotFound as cnf:
            raise HTTPException(status_code=400, detail=str(cnf))
        except UserNotFound as unf:
            raise HTTPException(status_code=400, detail=str(unf))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def is_user_in_conversation(self, user_id: str, conversation_id: str):
        if self.conversation_repository.is_conversation_cached(conversation_id):
            is_in = self.conversation_repository.is_user_in_cached_conversation(
                user_id=user_id, conversation_id=conversation_id
            )
            return is_in
        else:
            try:
                conversation = await self.get_conversation_by_user_and_conversation_id(
                    user_id=user_id, conversation_id=conversation_id
                )
                self.conversation_repository.cache_conversation_participants(
                    conversation_id=str(conversation.id),
                    participant_ids=[
                        str(participant.user_id)
                        for participant in conversation.participants
                    ],
                )
                return True
            except ConversationNotFound:
                return False

    async def get_private_conversation_by_another_user_id(
        self, user_id: str, current_user: UserRead
    ):
        conversation = await Conversation.aggregate(
            [
                {
                    "$match": {
                        "$and": [
                            {
                                "participants": {
                                    "$all": [
                                        {
                                            "$elemMatch": {
                                                "user_id": PydanticObjectId(user_id)
                                            }
                                        },
                                        {"$elemMatch": {"user_id": current_user.id}},
                                    ]
                                }
                            },
                            {"participants": {"$size": 2}},
                        ]
                    }
                },
                *conversation_participant_user_map,
            ],
            projection_model=ConversationWithLatestMessageAndUser,
        ).to_list()
        return conversation
