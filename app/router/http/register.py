from fastapi import APIRouter

from model.schemas import UserRegister
from service.user import UserService


class SignUpRouter(APIRouter):
    def __init__(self, user_service: UserService, prefix: str):
        super().__init__(prefix=prefix)
        self.user_service = user_service
        super().add_api_route("", self.register, methods=["POST"])

    async def register(self, user_register: UserRegister):
        return await self.user_service.register(user_register)
