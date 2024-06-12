from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from model.mongo import __beanie_models__
from util.setting import get_settings

settings = get_settings()
mongo_uri = (
    f"mongodb://{settings.mongo_host}:{settings.mongo_port}/{settings.mongo_port}"
)


async def initialize_mongo_with_beanie():
    client = AsyncIOMotorClient(mongo_uri)  # type: ignore[attr-defined]
    await init_beanie(client[settings.mongo_db_name], document_models=__beanie_models__)  # type: ignore[arg-type,attr-defined]
