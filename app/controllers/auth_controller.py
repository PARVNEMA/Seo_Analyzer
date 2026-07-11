"""Authentication business-logic controller.

Handles login (credential verification + token issuance) and
token refresh workflows.
"""

from __future__ import annotations

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.crud.user import user_crud
from app.schemas.auth import Token


class AuthController:
    """Business-logic layer for authentication operations."""

    @staticmethod
    async def login(db: AsyncSession, *, email: str, password: str) -> Token:
        """Authenticate a user and return JWT tokens.

        Args:
            db: Async database session.
            email: User email.
            password: Plain-text password.

        Returns:
            Token schema with access and refresh tokens.

        Raises:
            UnauthorizedException: If credentials are invalid.
        """
        user = await user_crud.authenticate(db, email=email, password=password)
        if user is None:
            raise UnauthorizedException(detail="Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedException(detail="Account is deactivated")

        return Token(
            access_token=create_access_token(subject=str(user.id)),
            refresh_token=create_refresh_token(subject=str(user.id)),
        )

    @staticmethod
    async def refresh_token(db: AsyncSession, *, token: str) -> Token:
        """Issue new tokens from a valid refresh token.

        Args:
            db: Async database session.
            token: The refresh JWT to validate.

        Returns:
            Token schema with new access and refresh tokens.

        Raises:
            UnauthorizedException: If the refresh token is invalid or
                the user no longer exists.
        """
        try:
            payload = verify_token(token)
        except JWTError:
            raise UnauthorizedException(detail="Invalid or expired refresh token")

        token_type = payload.get("type")
        if token_type != "refresh":
            raise UnauthorizedException(detail="Token is not a refresh token")

        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(detail="Invalid token payload")

        import uuid
        user = await user_crud.get(db, id=uuid.UUID(user_id))
        if user is None:
            raise UnauthorizedException(detail="User not found")
        if not user.is_active:
            raise UnauthorizedException(detail="Account is deactivated")

        return Token(
            access_token=create_access_token(subject=str(user.id)),
            refresh_token=create_refresh_token(subject=str(user.id)),
        )


# Singleton instance for convenience.
auth_controller = AuthController()
