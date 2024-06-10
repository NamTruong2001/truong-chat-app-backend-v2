from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.http.auth import AuthRouter
from router.http.conversation import ConversationRouter
from router.http.register import SignUpRouter
from service import ConversationService
from db.mongo import initialize_mongo_with_beanie
from service.user import UserService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await initialize_mongo_with_beanie()
    conversation_service = ConversationService()
    conversation_router = ConversationRouter(conversation_service)
    user_service = UserService()
    auth_router = AuthRouter(user_service)
    register_router = SignUpRouter(user_service)
    app.include_router(conversation_router.get_router(), prefix="/api/conversation")
    app.include_router(auth_router.get_router(), prefix="/api/auth")
    app.include_router(register_router.get_router(), prefix="/api/auth")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
