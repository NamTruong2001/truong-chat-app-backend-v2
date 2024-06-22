import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from repository import ConversationRepository
from repository.user import UserRepository
from router.http.auth import AuthRouter
from router.http.conversation import ConversationRouter
from router.http.message import MessageRouter
from router.http.register import SignUpRouter
from router.socket import ChatSocket
from service import ConversationService, MessageService
from db.mongo import initialize_mongo_with_beanie
from service.user import UserService
from db.redis import connect_to_redis_with_retry
from parser import args
from util import get_settings

fapp = FastAPI()
settings = get_settings()
fapp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mgr = socketio.AsyncRedisManager(
    f"redis://{settings.redis_user}:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}"
)
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    client_manager=mgr,
    engineio_logger=True,
)
app = socketio.ASGIApp(sio, fapp)
redis_client = connect_to_redis_with_retry()


@fapp.on_event("startup")
async def startup_event():
    # db
    await initialize_mongo_with_beanie()

    # repository
    user_repository = UserRepository(redis_client=redis_client)
    conversation_repository = ConversationRepository(redis_client=redis_client)

    # service
    conversation_service = ConversationService(
        conversation_repository=conversation_repository
    )
    user_service = UserService(user_repository=user_repository)
    message_service = MessageService(conversation_service=conversation_service)

    # router
    auth_router = AuthRouter(user_service=user_service, prefix="/api/auth")
    register_router = SignUpRouter(user_service=user_service, prefix="/api/register")
    conversation_router = ConversationRouter(
        conversation_service=conversation_service, prefix="/api/conversation"
    )
    message_router = MessageRouter(
        message_service=message_service, prefix="/api/message"
    )
    fapp.include_router(conversation_router)
    fapp.include_router(auth_router)
    fapp.include_router(register_router)
    fapp.include_router(message_router)

    # socket
    chat_socket = ChatSocket(
        name_space="/chat",
        chat_service=message_service,
        conversation_service=conversation_service,
        user_service=user_service,
    )
    sio.register_namespace(chat_socket)
    # test_router = TestRouter(prefix="/hehe")
    # app.include_router(test_router)


@fapp.on_event("shutdown")
def shutdown_event():
    redis_client.flushdb()
    redis_client.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=args.port, log_level="info", reload=True
    )
