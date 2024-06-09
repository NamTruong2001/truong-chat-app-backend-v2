from datetime import datetime

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    username: Indexed(str, unique=True)
    password: str
    email: Indexed(str, unique=True)
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "user"
        validate_on_save = True
