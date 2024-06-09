from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.http.conversation import ConversationRouter
from service import ConversationService
from db.mongo import initialize_mongo_with_beanie


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
    app.include_router(conversation_router.router, prefix="/api/conversation")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
