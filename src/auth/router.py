from typing import Annotated

from fastapi import APIRouter, Depends, Form, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import pbkdf2_sha256
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidCredentialsError, UserAlreadyExists
from src.auth.models import User
from src.auth.schemas import UserScheme
from src.auth.security import create_jwt_token
from src.database import get_async_session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.username == username)
    result = await session.scalar(stmt)
    if result:
        raise UserAlreadyExists

    password = pbkdf2_sha256.hash(password)
    new_user = User(username=username, password=password)
    session.add(new_user)
    await session.commit()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.post("/login")
async def login(
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.username == user_credentials.username)
    user = await session.scalar(stmt)

    if user is None or not pbkdf2_sha256.verify(
        user_credentials.password, user.password
    ):
        raise InvalidCredentialsError

    access_token = create_jwt_token({"sub": user_credentials.username})
    response = RedirectResponse("/todos?page=1", status_code=status.HTTP_302_FOUND)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600,
        expires=3600,
        secure=True,
        samesite="lax",
    )

    return response


@router.get("/exit")
async def exit():
    response = RedirectResponse(
        "/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
    response.delete_cookie("access_token")
    return response
