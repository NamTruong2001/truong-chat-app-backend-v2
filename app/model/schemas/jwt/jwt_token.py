from datetime import timedelta

from pydantic import BaseModel


class JWTToken(BaseModel):
    access_token: str
    # access_token_expires: timedelta


class RefreshToken(JWTToken):
    refresh_token: str
    refresh_expires_in: timedelta
