"""User business-logic controller.

Encapsulates user-related business rules and orchestrates calls to
the CRUD layer. Route handlers should delegate to this controller
rather than calling CRUD operations directly.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate


class UserController:
    """Business-logic layer for user operations."""

    @staticmethod
    async def get_user(db: AsyncSession, user_id: UUID) -> User:
        """Fetch a single user by ID.

        Raises:
            NotFoundException: If the user does not exist.
        """
        user = await user_crud.get(db, id=user_id)
        if user is None:
            raise NotFoundException(detail=f"User {user_id} not found")
        return user

    @staticmethod
    async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> UserListResponse:
        """Return a paginated list of users."""
        users = await user_crud.get_multi(db, skip=skip, limit=limit)
        total = await user_crud.count(db)
        return UserListResponse(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
        )

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        """Create a new user.

        Raises:
            ConflictException: If the email is already registered.
        """
        existing = await user_crud.get_by_email(db, email=user_in.email)
        if existing:
            raise ConflictException(
                detail=f"Email {user_in.email} is already registered"
            )
        return await user_crud.create(db, obj_in=user_in)

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        user_in: UserUpdate,
    ) -> User:
        """Update an existing user.

        Raises:
            NotFoundException: If the user does not exist.
            ConflictException: If the new email is already taken.
        """
        user = await user_crud.get(db, id=user_id)
        if user is None:
            raise NotFoundException(detail=f"User {user_id} not found")

        # Check for email uniqueness if email is being changed.
        if user_in.email and user_in.email != user.email:
            existing = await user_crud.get_by_email(db, email=user_in.email)
            if existing:
                raise ConflictException(
                    detail=f"Email {user_in.email} is already registered"
                )

        return await user_crud.update(db, db_obj=user, obj_in=user_in)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> User:
        """Delete a user.

        Raises:
            NotFoundException: If the user does not exist.
        """
        user = await user_crud.delete(db, id=user_id)
        if user is None:
            raise NotFoundException(detail=f"User {user_id} not found")
        return user


# Singleton instance for convenience.
user_controller = UserController()
