from redis import Redis


class UserRepository:
    def __init__(self, redis_client: Redis):
        self.__redis_client = redis_client
        self.online_users_key = "online_user_ids"
        self.user_sockets_key = "user:{}:socket_ids"

    async def add_online_user(self, user_id: str) -> int:
        return await self.__redis_client.sadd(self.online_users_key, user_id)

    async def remove_online_user(self, user_id: str) -> int:
        return await self.__redis_client.srem(self.online_users_key, user_id)

    async def is_user_online(self, user_id: str) -> bool:
        result = await self.__redis_client.sismember(self.online_users_key, user_id)
        return bool(result)

    async def add_user_socket(self, user_id: str, socket_id: str) -> int:
        result = await self.__redis_client.sadd(
            self.user_sockets_key.format(user_id), socket_id
        )
        return result

    async def remove_user_socket(self, user_id: str, socket_id: str) -> int:
        result = await self.__redis_client.srem(
            self.user_sockets_key.format(user_id), socket_id
        )
        return result

    async def get_user_sockets(self, user_id: str) -> set[str]:
        return await self.__redis_client.smembers(self.user_sockets_key.format(user_id))
