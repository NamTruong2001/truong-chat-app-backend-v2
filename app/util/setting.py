import sys
from functools import lru_cache
from pydantic_settings import SettingsConfigDict, BaseSettings
from parser import args


class Settings(BaseSettings):
    mongo_port: str
    mongo_user: str
    mongo_password: str
    mongo_host: str
    mongo_db_name: str
    jwt_secret_key: str
    jwt_algorithm: str
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str
    redis_user: str
    allowed_images_type: list[str] = [
        "image/png",
        "image/gif",
        "image/jpeg",
        "image/jpg",
    ]
    allowed_video_type: list[str] = ["video/mp4"]

    model_config = SettingsConfigDict(
        env_file=f".././.{args.environ if len(sys.argv) > 1 else 'local'}"
    )


@lru_cache()
def get_settings():
    # with open(".././.local", "r") as f:
    #     print(f.read())
    return Settings()
