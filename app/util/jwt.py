from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import ValidationError

from model.mongo import User
import jwt
from socketio.exceptions import ConnectionRefusedError

from model.schemas.user import UserRead
from util.setting import get_settings

settings = get_settings()
SECURITY_ALGORITHM = settings.jwt_algorithm
SECRET_KEY = settings.jwt_secret_key
EXPIRES_AFTER_MINUTES = 30

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


def validate_token(http_authorization_credentials=Depends(reusable_oauth2)) -> UserRead:
    try:
        payload = jwt.decode(
            http_authorization_credentials.credentials,
            SECRET_KEY,
            algorithms=[SECURITY_ALGORITHM],
        )
        return UserRead(
            id=payload.get("id"),
            email=payload.get("email"),
            username=payload.get("username"),
        )
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail=f"Could not validate credentials",
        )


def validate_socket_connection(auth_headers: dict) -> UserRead:
    try:
        if "HTTP_TOKEN" in auth_headers:
            token = auth_headers["HTTP_TOKEN"]
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[SECURITY_ALGORITHM],
            )
            return UserRead(
                id=payload.get("id"),
                email=payload.get("email"),
                username=payload.get("username"),
            )
        else:
            raise ConnectionRefusedError({"hehe": "hehe"})
    except (jwt.PyJWTError, ValidationError):
        raise ConnectionRefusedError("Can't validate token")


def generate_jwt_token(user_db: User):
    user_to_encode = {
        "id": str(user_db.id),
        "email": user_db.email,
        "username": user_db.username,
    }
    encoded_jwt = jwt.encode(user_to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)

    return encoded_jwt
