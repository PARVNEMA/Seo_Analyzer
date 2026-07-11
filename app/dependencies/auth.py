"""Authentication dependencies for FastAPI.

Provides reusable ``Depends()`` callables for JWT-based authentication
and role-based access control.
"""

from __future__ import annotations

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import verify_token
from app.crud.user import user_crud
from app.db.session import get_db
from app.models.user import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the JWT and return the corresponding ``User``.

    Raises:
        UnauthorizedException: If the token is invalid or the user
            does not exist.
    """
    try:
        payload = verify_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException(detail="Invalid token: missing subject")
    except JWTError:
        raise UnauthorizedException(detail="Invalid or expired token")

    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedException(detail="Invalid token: bad subject format")

    user = await user_crud.get(db, id=user_id)
    if user is None:
        raise UnauthorizedException(detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the current user only if their account is active.

    Raises:
        ForbiddenException: If the user account is deactivated.
    """
    if not current_user.is_active:
        raise ForbiddenException(detail="Inactive user account")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Return the current user only if they are a superuser.

    Raises:
        ForbiddenException: If the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise ForbiddenException(detail="Superuser access required")
    return current_user
