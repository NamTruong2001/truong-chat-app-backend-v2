from fastapi import HTTPException

from exceptions import UserNotFound
from repository.user import UserRepository
from schemas.enums import SocketAction
from schemas.jwt import JWTToken
from schemas.user import UserRead, LoginResult
from util.jwt import generate_jwt_token
from model.mongo import User
from schemas import UserLogin, UserRegister


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login(self, user_login: UserLogin) -> LoginResult:
        user = await User.find_one(
            {"$and": [{"email": user_login.email}, {"password": user_login.password}]}
        )
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        token = generate_jwt_token(user)
        jwt_token = JWTToken(access_token=token)
        return LoginResult(
            user=UserRead(id=user.id, email=user.email, username=user.username),
            credentials=jwt_token,
        )

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

    def _add_online_user(self, user_id: str):
        return self.user_repository.add_online_user(user_id)

    def _remove_online_user(self, user_id: str):
        return self.user_repository.remove_online_user(user_id)

    def manage_user_socket_connection(
        self, user_id: str, socket_id: str, connect_action: SocketAction
    ):
        user_connections = self.user_repository.get_user_sockets(user_id)
        if len(user_connections) >= 1 and connect_action == SocketAction.CONNECT:
            self.user_repository.add_user_socket(user_id=user_id, socket_id=socket_id)

        if len(user_connections) < 1 and connect_action == SocketAction.CONNECT:
            self.user_repository.add_online_user(user_id=user_id)
            self.user_repository.add_user_socket(user_id=user_id, socket_id=socket_id)

        if len(user_connections) > 1 and connect_action == SocketAction.DISCONNECT:
            self.user_repository.remove_user_socket(
                user_id=user_id, socket_id=socket_id
            )

        if len(user_connections) <= 1 and connect_action == SocketAction.DISCONNECT:
            self.user_repository.remove_online_user(user_id=user_id)
            self.user_repository.remove_user_socket_key(user_id)
        return self.user_repository.get_user_sockets(user_id)
