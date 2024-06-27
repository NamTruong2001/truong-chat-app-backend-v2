import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, PydanticObjectId
from model.mongo import (
    Message,
    User,
    Conversation,
    Participant,
    SystemMessage,
    UserMessage,
)
from bson import ObjectId
from db.mongo import initialize_mongo_with_beanie
from enums import SystemMessageType, UserMessageType

settings = {"db_name": "chat_app_testing", "uri": "mongodb://localhost:27017"}


async def data_test_for_conversation():
    client = AsyncIOMotorClient(settings["uri"])
    await init_beanie(
        database=client.chat_testing,
        document_models=[Message, User, Conversation],
    )
    user1 = await User.find_one(User.username == "User1")
    if user1 is None:
        user1 = User(
            username="User1", email="user1@gmail.com", password="123456", is_active=True
        )
        await user1.insert()
    user2 = await User.find_one(User.username == "User2")
    if user2 is None:
        user2 = User(
            username="User2", email="user2@gmail.com", password="123456", is_active=True
        )
        await user2.insert()
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


async def init_test_data():
    client = AsyncIOMotorClient(settings["uri"])
    await init_beanie(
        database=client.chat_testing,
        document_models=[Message, User, Conversation],
    )
    user1 = User(
        username="User1", email="user1@gmail.com", password="123456", is_active=True
    )
    await user1.insert()
    user2 = User(
        username="User2", email="user2@gmail.com", password="123456", is_active=True
    )
    await user2.insert()
    user3 = User(
        username="User3", email="user3@gmail.com", password="123456", is_active=True
    )
    await user3.insert()
    participant1 = Participant(user_id=user1.id)
    participant2 = Participant(user_id=user2.id)
    conversation1 = Conversation(
        title="Test Conversation",
        creator=user1,
        participants=[participant1, participant2],
        type="private",
    )
    await conversation1.insert()

    conversation2 = Conversation(
        title="Test Conversation",
        creator=user1,
        participants=[participant1, Participant(user_id=user3.id)],
        type="private",
    )
    await conversation2.insert()

    message = [
        UserMessage(
            conversation_id=conversation1.id,
            sender_id=user1.id,
            type=UserMessageType.TEXT,
            content="Hello from user 1",
        ),
        UserMessage(
            conversation_id=conversation1.id,
            sender_id=user2.id,
            type=UserMessageType.TEXT,
            content="Hi from user 2",
        ),
        UserMessage(
            conversation_id=conversation2.id,
            sender_id=user3.id,
            type=UserMessageType.TEXT,
            content="Hi from user 3",
        ),
        UserMessage(
            conversation_id=conversation2.id,
            sender_id=user2.id,
            type=UserMessageType.TEXT,
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

    async def generate_system_messages():
        # generate some messages of type SystemMessage
        client = AsyncIOMotorClient(settings["uri"])
        await init_beanie(
            database=client.chat_testing,
            document_models=[Message, User, Conversation, UserMessage, SystemMessage],
        )
        s = SystemMessage(
            conversation_id=PydanticObjectId("666becdad41278ef87be0837"),
            system_type=SystemMessageType.SYSTEM_TEXT,
            system_content={"message": "Hello"},
        )
        await s.insert()

    asyncio.run(generate_system_messages())
