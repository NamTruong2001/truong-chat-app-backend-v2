import asyncio
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, WriteRules, PydanticObjectId
from model.mongo import Message, User, Conversation, Participant, Attachment
from bson import ObjectId
from db.mongo import initialize_mongo_with_beanie
from service import ConversationService

settings = {"db_name": "chat_app_testing", "uri": "mongodb://localhost:27017"}


async def data_test():
    client = AsyncIOMotorClient(settings["uri"])
    await init_beanie(
        database=client.chat_testing,
        document_models=[Message, User, Conversation],
    )

    # user1 = User(
    #     username="User1",
    #     email="user1@gmail.com",
    #     password="password",
    #     is_active=True,
    # )
    # user2 = User(
    #     username="User2",
    #     email="user2@gmail.com",
    #     password="password",
    #     is_active=True,
    # )
    user1 = await User.find_one(User.username == "User1")
    user2 = await User.find_one(User.username == "User2")
    participant1 = Participant(user_id=user1.id)
    participant2 = Participant(user_id=user2.id)
    conversation = Conversation(
        title="Test Conversation",
        creator=user1,
        participants=[participant1, participant2],
        type="private",
    )
    await conversation.insert()


async def get_conversation_that_include_participant():
    client = AsyncIOMotorClient(settings["uri"])
    await init_beanie(
        database=client.chat_testing,
        document_models=[Message, User, Conversation],
    )
    conversation = {
        "participants.user_id.$ref": "User",
        "participants.user_id.$id": "66628dec0b03778aacea99fa",
    }
    conversation = await Conversation.find(
        {
            "participants.user_id.$ref": "User",
            "participants.user_id.$id": ObjectId("66628dec0b03778aacea99fa"),
        }
    ).to_list()
    print(conversation)
    # for participant in conversation[0].participants:
    #     user = await participant.user.fetch()
    #     print(user)


async def test_data_for_message():
    client = AsyncIOMotorClient(settings["uri"])
    await init_beanie(
        database=client.chat_testing,
        document_models=[Message, User, Conversation],
    )
    user1 = await User.find_one(User.username == "User1")
    user2 = await User.find_one(User.username == "User2")
    user3 = await User.find_one(User.username == "User3")
    conversation1 = await Conversation.find_one(
        Conversation.id == PydanticObjectId("66649e1747a0f6ecd6c14160")
    )
    conversation2 = await Conversation.find_one(
        Conversation.id == PydanticObjectId("666571a5085e310b634fb7e9")
    )
    message = [
        Message(
            conversation_id=conversation1.id,
            sender_id=user1.id,
            type="text",
            content="Hello from user 1",
        ),
        Message(
            conversation_id=conversation1.id,
            sender_id=user2.id,
            type="text",
            content="Hi from user 2",
        ),
        Message(
            conversation_id=conversation2.id,
            sender_id=user3.id,
            type="text",
            content="Hi from user 3",
        ),
        Message(
            conversation_id=conversation2.id,
            sender_id=user2.id,
            type="text",
            content="Hi from user 1",
        ),
    ]

    res = await Message.insert_many(message)
    print(res)


async def get_messages():
    client = AsyncIOMotorClient(settings["uri"])
    await init_beanie(
        database=client.chat_testing,
        document_models=[Message, User, Conversation],
    )
    messages = await Message.find(
        {"_id": {"$in": [ObjectId("66657580dcfe6c87ccc6fc62")]}}
    ).to_list()
    print(messages)
    for message in messages:
        print(message)


if __name__ == "__main__":

    async def run():
        await initialize_mongo_with_beanie()
        user = await User.find_one(User.username == "User1")
        print(user)

    asyncio.run(run())
