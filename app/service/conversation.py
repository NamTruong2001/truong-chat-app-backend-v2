from beanie import PydanticObjectId
from beanie.odm.operators.find.comparison import In
from bson import ObjectId
from fastapi import HTTPException

from model.mongo import Conversation, Participant, User
from exceptions import (
    ConversationNotFound,
    UserNotFound,
    ParticipantAlreadyExists,
    ParticipantNotFound,
)
from repository import ConversationRepository
from schemas.conversation import ConversationWithLatestMessage
from schemas.enums import ConversationEnum
from schemas.user import UserRead


class ConversationService:
    def __init__(self, conversation_repository: ConversationRepository):
        self.conversation_repository = conversation_repository
        pass

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
            raise HTTPException(status_code=400, detail="Conversation not found")
        return conversation

    async def get_user_conversation_sort_by_latest_message(self, user: UserRead):
        """
        :param user:
        :return:
         group message by conversation id and by max created_at
        filter conversation of that user and join with max created_at message by conversation_id
        """
        conversations = await Conversation.aggregate(
            [
                {
                    "$match": {
                        "participants": {
                            "$elemMatch": {"user_id": PydanticObjectId(user.id)}
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "Message",
                        "let": {"conversationId": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$conversation_id", "$$conversationId"]
                                    }
                                }
                            },
                            {"$sort": {"created_at": -1}},
                            {"$limit": 1},
                        ],
                        "as": "latest_message",
                    }
                },
                {
                    "$addFields": {
                        "newestMessage": {"$arrayElemAt": ["$latest_message", 0]}
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "title": 1,
                        "creator": 1,
                        "created_at": 1,
                        "deleted_at": 1,
                        "type": 1,
                        "participants": 1,
                        "latest_message": 1,
                    }
                },
                {"$sort": {"latest_message.created_at": -1}},
            ],
            projection_model=ConversationWithLatestMessage,
        ).to_list()
        return conversations

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

    async def add_participant(
        self, conversation_id: str, add_user_ids: list[str], current_user: UserRead
    ):
        try:
            # add_user = await User.find_one(User.id == PydanticObjectId(add_user_id))
            # if add_user is None:
            #     raise UserNotFound(add_user_id)
            conversation = await self.get_conversation_by_user_and_conversation_id(
                conversation_id=conversation_id, user_id=str(current_user.id)
            )
            added_participants = conversation.add_participant(add_user_ids)
            if not added_participants:
                raise ParticipantAlreadyExists("Participants already exist")
            await conversation.save()
            if self.conversation_repository.is_conversation_cached(conversation_id):
                self.conversation_repository.add_user_id_to_conversation(
                    conversation_id=conversation_id, user_id=add_user_ids
                )
            return conversation
        except ParticipantAlreadyExists as pae:
            raise HTTPException(status_code=400, detail=str(pae))
        except ConversationNotFound as cnf:
            raise HTTPException(status_code=400, detail=str(cnf))
        except UserNotFound as unf:
            raise HTTPException(status_code=400, detail=str(unf))

    async def remove_participant(
        self, conversation_id: str, remove_user_ids: list[str], current_user: UserRead
    ):
        try:
            conversation = await self.get_conversation_by_user_and_conversation_id(
                conversation_id=conversation_id, user_id=str(current_user.id)
            )
            removed_participants = conversation.remove_participant(remove_user_ids)
            if not removed_participants:
                raise ParticipantNotFound("Participants not found")
            await conversation.save()
            if self.conversation_repository.is_conversation_cached(conversation_id):
                self.conversation_repository.remove_user_id_from_conversation(
                    conversation_id=conversation_id, user_id=remove_user_ids
                )
            return conversation
        except ParticipantNotFound as pnf:
            raise HTTPException(status_code=400, detail=str(pnf))
        except ConversationNotFound as cnf:
            raise HTTPException(status_code=400, detail=str(cnf))
        except UserNotFound as unf:
            raise HTTPException(status_code=400, detail=str(unf))

    async def get_user_conversations(
        self, user_id: str, conversation_type: ConversationEnum, is_all: bool = False
    ):
        if is_all is True:
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
        conversation = await Conversation.find(
            {
                "$and": [
                    {
                        "participants": {
                            "$all": [
                                {"$elemMatch": {"user_id": PydanticObjectId(user_id)}},
                                {"$elemMatch": {"user_id": current_user.id}},
                            ]
                        }
                    },
                    {"participants": {"$size": 2}},
                ]
            }
        ).first_or_none()
        return conversation
