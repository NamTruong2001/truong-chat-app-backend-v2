from socketio import AsyncNamespace

from service import ConversationService, ChatService


class ChatSocket(AsyncNamespace):
    def __init__(
        self,
        name_space: str,
        chat_service: ChatService,
        conversation_service: ConversationService,
    ):
        super().__init__(name_space)
        self.chat_service = chat_service
        self.conversation_service = conversation_service

    async def on_connect(self, sid, auth, environment):
        print("Connected")
        print(sid)

    async def on_message(self, sid, data):
        print("Message")
        print(sid)
        print(data)
        await self.emit("message", data)

    async def on_disconnect(self, sid):
        print("Disconnected")
        print(sid)
