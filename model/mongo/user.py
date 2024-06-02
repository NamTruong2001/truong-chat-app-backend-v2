from datetime import datetime

from odmantic import Model


class User(Model):
    username: str
    password: str
    email: str
    is_active: bool
    created_at: datetime
