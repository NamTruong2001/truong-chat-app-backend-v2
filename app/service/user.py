from fastapi import HTTPException

from exceptions import UserNotFound
from schemas.user import UserRead
from util.jwt import generate_jwt_token
from model.mongo import User
from schemas import UserLogin, UserRegister


class UserService:
    def __init__(self):
        pass

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
