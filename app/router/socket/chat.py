from socketio import AsyncNamespace


class ChatSocket(AsyncNamespace):
    def __init__(self, name_space: str):
        super().__init__(name_space)

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
