from beanie import PydanticObjectId
from redis import Redis

from model.mongo import User


class UserRepository:
    def __init__(self, redis_client: Redis):
        self.__redis_client = redis_client
        self.online_users_key = "online_user_ids"
        self.user_sockets_key = "user:{}:socket_ids"

    def add_online_user(self, user_id: str) -> int:
        return self.__redis_client.sadd(self.online_users_key, user_id)

    def remove_online_user(self, user_id: str) -> int:
        return self.__redis_client.srem(self.online_users_key, user_id)

    def remove_user_socket_key(self, user_id: str) -> int:
        return self.__redis_client.delete(self.user_sockets_key.format(user_id))

    def is_user_online(self, user_id: str) -> bool:
        result = self.__redis_client.sismember(self.online_users_key, user_id)
        return bool(result)

    def add_user_socket(self, user_id: str, socket_id: str) -> int:
        result = self.__redis_client.sadd(
            self.user_sockets_key.format(user_id), socket_id
        )
        return result

    def remove_user_socket(self, user_id: str, socket_id: str) -> int:
        result = self.__redis_client.srem(
            self.user_sockets_key.format(user_id), socket_id
        )
        return result

    def get_user_sockets(self, user_id: str) -> set[str]:
        return self.__redis_client.smembers(self.user_sockets_key.format(user_id))

    async def get_many_users(self, user_ids: list[PydanticObjectId]) -> list[User]:
        users = await User.find({"_id": {"$in": user_ids}}).to_list()
        return users
