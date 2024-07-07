from redis.asyncio import Redis

from model.schemas import CacheConversation


class ConversationRepository:
    def __init__(self, redis_client: Redis):
        self.__rc = redis_client
        self.conversation_participants_key = "conversation:{}:participants"
        self.conversation_type_key = "conversation:{}:type"
        self.conversation_key = "conversation:{}"

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

    def cache_conversation(self, conversation: CacheConversation):
        self.__rc.json().set(
            name=self.conversation_key.format(conversation.id),
            path=".",
            obj=conversation.model_dump(),
        )
        self.__rc.expire(self.conversation_key.format(conversation.id), 2 * 60 * 60)

    def get_cache_conversation(self, conversation_id: str) -> dict:
        return self.__rc.json().get(name=self.conversation_key.format(conversation_id))
