class MessageNotFound(Exception):
    def __init__(self, message_id):
        self.message_id = message_id
        self.message = f"Message with id {message_id} not found"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class MessageSentError(Exception):
    def __init__(self, message: str, conversation: dict):
        self.message = message
        self.conversation = conversation

    def __str__(self):
        return self.message
