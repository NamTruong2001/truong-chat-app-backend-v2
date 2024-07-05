# import all the models here
from .conversation import Conversation, Participant
from .user import User
from .message import Message, Attachment, UserMessage, SystemMessage
from .read_status import ReadStatus

__beanie_models__ = [
    User,
    Conversation,
    Message,
    UserMessage,
    SystemMessage,
    ReadStatus,
]
