from redis import Redis


class UserRepository:
    def __init__(self, redis_client: Redis):
        self.__redis_client = redis_client
        self.online_users_key = "online_users"

    def add_online_user(self, user_id: str):
        self.__redis_client.sadd(self.online_users_key, user_id)

    def remove_online_user(self, user_id: str):
        self.__redis_client.srem(self.online_users_key, user_id)

    def is_user_online(self, user_id: str) -> bool:
        return bool(self.__redis_client.sismember(self.online_users_key, user_id))
