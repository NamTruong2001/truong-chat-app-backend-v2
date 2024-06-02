from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine


class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self._uri = uri
        self._db_name = db_name
        self._client = None
        self._engine = None

    def connect(self):
        try:
            self._client = AsyncIOMotorClient(self._uri, maxPoolSize=10, minPoolSize=4)
            self._engine = AIOEngine(client=self._client, database="chat-app-testing")
        except ConnectionError as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    def get_engine(self):
        if self._engine is None:
            self.connect()
        return self._engine

    def close(self):
        if self._client:
            self._client.close()
