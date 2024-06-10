from beanie import PydanticObjectId
from bson import ObjectId

from model.mongo import Conversation, Participant, User
from exceptions import ConversationNotFound, UserNotFound
from schemas import ConversationWithLatestMessage


class ConversationService:
    def __init__(self):
        pass

    async def get_conversation_by_user_and_conversation_id(
        self, user_id: str, conversation_id: str
    ):
        conversations = await Conversation.find(
            {
                "$and": [
                    {"_id": ObjectId(conversation_id)},
                    {"participants": {"$elemMatch": {"user_id": ObjectId(user_id)}}},
                ]
            }
        ).to_list()
        if not conversations:
            raise ConversationNotFound(conversation_id)
        return conversations

    async def get_user_conversation_sort_by_latest_message(self, user_id: str):
        """
        :param user_id:
        :return:
         group message by conversation id and by max created_at
        filter conversation of that user and join with max created_at message by conversation_id
        """
        conversations = await Conversation.aggregate(
            [
                {
                    "$match": {
                        "participants": {
                            "$elemMatch": {"user_id": PydanticObjectId(user_id)}
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
        print(conversations)
        return conversations

    async def create_conversation(
        self,
        title: str,
        creator_id: str,
        conversation_type: str,
        participant_ids: list[str],
    ):
        creator = User.find_one(User.id == PydanticObjectId(creator_id))
        if creator is None:
            raise UserNotFound(creator_id)
        participants = [
            Participant(user_id=participant_id) for participant_id in participant_ids
        ]
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
