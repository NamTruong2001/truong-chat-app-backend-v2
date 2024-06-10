from fastapi import APIRouter

from schemas import UserLogin
from service.user import UserService


class AuthRouter:
    def __init__(self, user_service: UserService):
        self._api_router = APIRouter()
        self.user_service = user_service
        self._api_router.add_api_route("/login", self.login, methods=["POST"])
        self._api_router.add_api_route("/logout", self.logout, methods=["POST"])
        self._api_router.add_api_route("/refresh", self.refresh, methods=["POST"])

    async def login(self, user_login: UserLogin):
        user = await self.user_service.login(user_login)
        return user

    async def logout(self, request):
        pass

    async def refresh(self, request):
        pass

    def get_router(self):
        return self._api_router
