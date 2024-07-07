from model.mongo import Conversation
from model.schemas import CacheConversation


def map_conversation_to_cache_conversation(
    conversation: Conversation,
) -> CacheConversation:
    cache_conversation = {
        "id": str(conversation.id),
        "title": conversation.title,
        "type": conversation.type,
        "creator_id": conversation.creator.to_dict()["id"],
        "created_at": str(conversation.created_at),
        "participants": [
            str(participant.user_id) for participant in conversation.participants
        ],
    }
    return CacheConversation(**cache_conversation)
