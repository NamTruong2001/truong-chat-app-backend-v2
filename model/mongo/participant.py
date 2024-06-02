from datetime import datetime

from odmantic import EmbeddedModel, ObjectId


class Participant(EmbeddedModel):
    user_id: ObjectId
    joined_at: datetime
