from fastapi import APIRouter

from schemas import UserRegister
from service.user import UserService


class SignUpRouter:
    def __init__(self, user_service: UserService):
        self._api_router = APIRouter()
        self.user_service = user_service
        self._api_router.add_api_route("/register", self.register, methods=["POST"])

    async def register(self, user_register: UserRegister):
        return await self.user_service.register(user_register)

    def get_router(self):
        return self._api_router
