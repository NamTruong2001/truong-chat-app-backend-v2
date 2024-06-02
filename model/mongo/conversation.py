from datetime import datetime
from odmantic import Model
from typing import List
from participant import Participant


class Conversation(Model):
    title: str
    creator_id: str
    created_at: datetime
    deleted_at: datetime
    type: str
    participants: List[Participant]
