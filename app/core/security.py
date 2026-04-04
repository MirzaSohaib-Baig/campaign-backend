from datetime import datetime, timedelta
import datetime as maintime
from typing import Dict, Optional, Union

import jwt
import structlog
from fastapi.requests import Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from passlib.context import CryptContext

from app.config.settings import settings
from app.core.exceptions import AuthError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

LOG = structlog.get_logger()


def hash_password(password: str):
    hashed = pwd_context.hash(password)
    return hashed


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> (str, str):
    if expires_delta:
        expire = datetime.now(maintime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(maintime.timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    payload = {"expires_at": expire.isoformat(), **data}
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    expiration_datetime = expire.isoformat()
    return encoded_jwt, expiration_datetime

# def create_access_token(
#     data: dict, expires_delta: Union[timedelta, None] = None
# ) -> str:
#     now = datetime.now(maintime.timezone.utc)
#     if expires_delta:
#         expire = now + expires_delta
#     else:
#         expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

#     payload = {
#         "exp": expire,
#         "iat": now,
#         **data
#     }
#     encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt



def generate_access_token(user: Dict) -> (str, str):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={
            "id": str(user.get("id")),
            "type": "access",
            },
        expires_delta=access_token_expires
    )


def generate_refresh_token(user: Dict) -> (str, str):
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(
        data={"id": str(user.get("id")), "type": "refresh"}, expires_delta=refresh_token_expires
    )


def decode_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=settings.ALGORITHM
        )

        expires_at = datetime.fromisoformat(decoded_token["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=maintime.timezone.utc)

        return decoded_token if expires_at >= datetime.now(maintime.timezone.utc) else None
    except Exception as e:
        LOG.error(e)
        return {}

# def decode_token(token: str) -> dict:
#     try:
#         decoded_token = jwt.decode(
#             token,
#             settings.JWT_SECRET_KEY,
#             algorithms=settings.ALGORITHM
#         )
#         return decoded_token
#     except jwt.ExpiredSignatureError:
#         LOG.error("Token has expired.")
#         return {}
#     except jwt.InvalidTokenError:
#         LOG.error("Invalid token.")
#         return {}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        # self.allowed_roles = allowed_roles

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AuthError(detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise AuthError(detail="Invalid or expired token.")
            request.state.user = decode_token(credentials.credentials)
            return credentials.credentials
        else:
            raise AuthError(detail="Invalid authorization code.")

    # async def __call__(self, request: Request):
    #     token = request.cookies.get("access_token") or request.cookies.get("refresh_token")
    #     if not token:
    #         raise AuthError("Missing token in cookie.")

    #     if not self.verify_jwt(token):
    #         raise AuthError("Invalid or expired token.")

    #     request.state.user = decode_token(token)
    #     return token


    def verify_jwt(self, jwt_token: str) -> bool:
        try:
            payload = decode_token(jwt_token)
        except Exception as e:
            LOG.error(e)
            return False

        if payload.get("type") != "access":
            return False
        
        if payload.get("expires_at") is None:
            return False

        expires_at: Optional[datetime] = datetime.fromisoformat(
            payload.get("expires_at")
        )
        if expires_at is None:
            return False

        return expires_at > datetime.now(maintime.timezone.utc)
