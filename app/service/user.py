from fastapi import HTTPException

from exceptions import UserNotFound
from repository.user_repository import UserRepository
from schemas.user import UserRead
from util.jwt import generate_jwt_token
from model.mongo import User
from schemas import UserLogin, UserRegister


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login(self, user_login: UserLogin):
        user = await User.find_one(
            {"$and": [{"email": user_login.email}, {"password": user_login.password}]}
        )
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        token = generate_jwt_token(user)
        return {"token": token}

    async def register(self, user_register: UserRegister):
        user = await User.find_one({"email": user_register.email})
        if user is not None:
            raise HTTPException(status_code=400, detail="Email already exists")
        new_user = User(
            email=user_register.email,
            password=user_register.password,
            username=user_register.username,
            is_active=True,
        )
        await new_user.insert()
        return UserRead(
            id=new_user.id, email=new_user.email, username=new_user.username
        )

    def is_user_online(self, user_id: str) -> bool:
        return self.user_repository.is_user_online(user_id)

    def add_online_user(self, user_id: str):
        self.user_repository.add_online_user(user_id)

    def remove_online_user(self, user_id: str):
        self.user_repository.remove_online_user(user_id)
