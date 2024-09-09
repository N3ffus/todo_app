from typing import Annotated

import jwt
from fastapi import Depends, Request

from src.auth.constants import ALGORITHM
from src.auth.exceptions import InvalidTokenError, TokenExpiredError
from src.auth.utils import OAuth2PasswordBearerWithCookie
from src.config import settings

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="auth/login")


def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError
    except jwt.InvalidSignatureError:
        raise InvalidTokenError


def is_authorized(request: Request) -> str:
    token = request.cookies.get("access_token")

    if not token:
        return False

    token = token.split()[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidSignatureError:
        return False
