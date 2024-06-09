class ConversationNotFound(Exception):
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.message = f"Conversation with id {conversation_id} not found"
        super().__init__(self.message)

    def __str__(self):
        return self.message
