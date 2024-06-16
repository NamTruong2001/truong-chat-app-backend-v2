from redis.asyncio import Redis


class ConversationRepository:
    def __init__(self, redis_client: Redis):
        self.__rc = redis_client
        self.conversation_participants_key = "conversation:{}:participants"

    async def is_conversation_cached(self, conversation_id: str) -> bool:
        result = await self.__rc.exists(
            self.conversation_participants_key.format(conversation_id)
        )
        return bool(result)

    async def cache_conversation_participants(
        self, conversation_id: str, participant_ids: list[str]
    ) -> int:
        formatted_key = self.conversation_participants_key.format(conversation_id)
        await self.__rc.sadd(formatted_key, *participant_ids)
        await self.__rc.expire(formatted_key, 1 * 60 * 60)

    async def is_user_in_cached_conversation(
        self, conversation_id: str, user_id: str
    ) -> bool:
        result = await self.__rc.sismember(
            self.conversation_participants_key.format(conversation_id), user_id
        )
        return bool(result)
