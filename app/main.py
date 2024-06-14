from contextlib import asynccontextmanager

import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from repository.user_repository import UserRepository
from router.http.auth import AuthRouter
from router.http.conversation import ConversationRouter
from router.http.register import SignUpRouter
from router.http.test import TestRouter
from router.socket import ChatSocket
from service import ConversationService, ChatService
from db.mongo import initialize_mongo_with_beanie
from service.user import UserService
from db.redis import connect_to_redis_with_retry

fapp = FastAPI()

fapp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mgr = socketio.AsyncRedisManager()
sio = socketio.AsyncServer(
    cors_allowed_origins="*", async_mode="asgi", client_manager=mgr
)
app = socketio.ASGIApp(sio, fapp)


@fapp.on_event("startup")
async def startup_event():
    # db
    await initialize_mongo_with_beanie()
    redis_client = connect_to_redis_with_retry()

    # repository
    user_repository = UserRepository(redis_client=redis_client)

    # service
    conversation_service = ConversationService()
    user_service = UserService(user_repository=user_repository)
    conversation_router = ConversationRouter(
        conversation_service=conversation_service, prefix="/api/conversation"
    )
    chat_service = ChatService()

    # router
    auth_router = AuthRouter(user_service=user_service, prefix="/api/auth")
    register_router = SignUpRouter(user_service=user_service, prefix="/api/register")
    fapp.include_router(conversation_router)
    fapp.include_router(auth_router)
    fapp.include_router(register_router)

    # socket
    chat_socket = ChatSocket(
        name_space="/chat",
        chat_service=chat_service,
        conversation_service=conversation_service,
        user_service=user_service,
    )
    sio.register_namespace(chat_socket)
    # test_router = TestRouter(prefix="/hehe")
    # app.include_router(test_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
