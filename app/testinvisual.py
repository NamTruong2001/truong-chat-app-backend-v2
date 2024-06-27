if __name__ == "__main__":
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
    laugh = {
        "hehe": {"laugh": "haha"},
        "criteria": conversation_with_latest_message_map,
        "mnoooo": [1, 2, 3, 3],
    }
