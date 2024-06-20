conversation_participant_user_map = [
    {"$unwind": "$participants"},
    {
        "$lookup": {
            "from": "User",
            "localField": "participants.user_id",
            "foreignField": "_id",
            "as": "user_details",
        }
    },
    {"$addFields": {"participants.user": {"$arrayElemAt": ["$user_details", 0]}}},
    {
        "$addFields": {
            "participants.user.id": "$participants.user._id",
        }
    },
    {
        "$group": {
            "_id": "$_id",
            "participants": {"$push": "$participants"},
            "title": {"$first": "$title"},
            "creator": {"$first": "$creator"},
            "created_at": {"$first": "$created_at"},
            "type": {"$first": "$type"},
        }
    },
    {
        "$project": {
            "participants.user.password": 0,
            "participants.user.is_active": 0,
            "participants.user.created_at": 0,
            "participants.user_id": 0,
            "participants.user._id": 0,
        }
    },
]

conversation_with_latest_message_map = [
    {
        "$lookup": {
            "from": "Message",
            "let": {"conversationId": "$_id"},
            "pipeline": [
                {
                    "$match": {
                        "$expr": {"$eq": ["$conversation_id", "$$conversationId"]}
                    }
                },
                {"$sort": {"created_at": -1}},
                {"$limit": 1},
            ],
            "as": "latest_message",
        }
    },
]
