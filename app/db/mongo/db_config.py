from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from model.mongo import __beanie_models__


settings = {"db_name": "chat_testing", "uri": "mongodb://localhost:27017"}


async def initialize_mongo_with_beanie():
    client = AsyncIOMotorClient(settings["uri"])  # type: ignore[attr-defined]
    await init_beanie(client[settings["db_name"]], document_models=__beanie_models__)  # type: ignore[arg-type,attr-defined]
