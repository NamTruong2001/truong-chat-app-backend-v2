from fastapi import APIRouter

from model.schemas import UserLogin
from service.user import UserService


class AuthRouter(APIRouter):
    def __init__(self, user_service: UserService, prefix: str):
        # self._api_router = APIRouter(prefix="/api/auth")
        super().__init__(prefix=prefix)
        self.user_service = user_service
        super().add_api_route("/login", self.login, methods=["POST"])
        super().add_api_route("/logout", self.logout, methods=["POST"])
        super().add_api_route("/refresh", self.refresh, methods=["POST"])

    async def login(self, user_login: UserLogin):
        user = await self.user_service.login(user_login)
        return user

    async def logout(self, request):
        pass

    async def refresh(self, request):
        pass
