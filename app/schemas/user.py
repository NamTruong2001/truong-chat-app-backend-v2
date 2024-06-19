from beanie import PydanticObjectId
from pydantic import BaseModel
from .jwt import JWTToken


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


class LoginResult(BaseModel):
    user: UserRead
    credentials: JWTToken
