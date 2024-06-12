import sys
from functools import lru_cache

from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    mongo_port: str
    mongo_user: str
    mongo_password: str
    mongo_host: str
    mongo_db_name: str
    jwt_secret_key: str
    jwt_algorithm: str
    redis_host: str
    redis_port: str
    redis_db: str
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
        env_file=f".././.{sys.argv[1] if len(sys.argv) > 1 else 'local'}"
    )


@lru_cache()
def get_settings():
    # with open(".././.local", "r") as f:
    #     print(f.read())
    return Settings()
