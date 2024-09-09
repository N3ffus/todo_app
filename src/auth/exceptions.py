from fastapi import HTTPException, status


class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            detail="User with this username already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class TokenExpiredError(HTTPException):
    def __init__(self):
        super().__init__(
            detail="The token has expired or the expiration date is incorrect!",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Invalid token!", status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Invalid credentials!",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
