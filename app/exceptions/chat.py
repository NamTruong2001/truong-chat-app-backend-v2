class MessageSentError(Exception):
    def __init__(self, message: str, conversation: dict):
        self.message = message
        self.conversation = conversation

    def __str__(self):
        return self.message
