from redis.asyncio import Redis


class ConversationRepository:
    def __init__(self, redis_client: Redis):
        self.__rc = redis_client
        self.conversation_participants_key = "conversation:{}:participants"

    def is_conversation_cached(self, conversation_id: str) -> bool:
        result = self.__rc.exists(
            self.conversation_participants_key.format(conversation_id)
        )
        return bool(result)

    def cache_conversation_participants(
        self, conversation_id: str, participant_ids: list[str]
    ):
        formatted_key = self.conversation_participants_key.format(conversation_id)
        self.__rc.sadd(formatted_key, *participant_ids)
        self.__rc.expire(formatted_key, 1 * 60 * 60)

    def is_user_in_cached_conversation(
        self, conversation_id: str, user_id: str
    ) -> bool:
        result = self.__rc.sismember(
            self.conversation_participants_key.format(conversation_id), user_id
        )
        return bool(result)

    def add_user_id_to_conversation(
        self, conversation_id: str, user_id: list[str]
    ) -> int:
        return self.__rc.sadd(
            self.conversation_participants_key.format(conversation_id), *user_id
        )

    def remove_user_id_from_conversation(
        self, conversation_id: str, user_id: list[str]
    ) -> int:
        return self.__rc.srem(
            self.conversation_participants_key.format(conversation_id), *user_id
        )
