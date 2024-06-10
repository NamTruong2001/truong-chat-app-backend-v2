from beanie import PydanticObjectId
from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    id: PydanticObjectId
    email: str
    username: str
