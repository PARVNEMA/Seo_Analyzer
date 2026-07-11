"""Authentication Pydantic schemas.

Defines models for JWT tokens and login requests.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT token pair returned after successful authentication.

    Attributes:
        access_token: Short-lived access JWT.
        refresh_token: Long-lived refresh JWT.
        token_type: Token scheme, always ``"bearer"``.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload.

    Attributes:
        sub: Subject — typically the user ID as a string.
        exp: Expiration datetime of the token.
    """

    sub: str
    exp: datetime


class LoginRequest(BaseModel):
    """Credentials submitted for login.

    Attributes:
        email: User email address.
        password: Plain-text password.
    """

    email: EmailStr
    password: str = Field(..., min_length=1)
