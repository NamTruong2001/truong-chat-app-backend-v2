from typing import Union

from odmantic import Model, ObjectId
from attachment import Attachment


class Message(Model):
    conversation_id: ObjectId
    sender_id: ObjectId
    message_type: str
    content: str
    created_at: str
    attachment: Union[None, Attachment]
