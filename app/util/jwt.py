from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import ValidationError

from model.mongo import User
import jwt

from schemas.user import UserRead

SECURITY_ALGORITHM = "HS256"
SECRET_KEY = "truongnn"
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


def generate_jwt_token(user_db: User):
    user_to_encode = {
        "id": str(user_db.id),
        "email": user_db.email,
        "username": user_db.username,
    }
    encoded_jwt = jwt.encode(user_to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)

    return encoded_jwt
