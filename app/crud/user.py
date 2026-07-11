"""User CRUD operations.

Extends ``CRUDBase`` with user-specific methods such as email lookup,
password-hashed creation, and authentication.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for the ``User`` model."""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            db: Async database session.
            email: The email to search for.

        Returns:
            The ``User`` instance or ``None``.
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user with a hashed password.

        Args:
            db: Async database session.
            obj_in: User creation schema (contains plain-text password).

        Returns:
            The newly created ``User`` instance.
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=hash_password(obj_in.password),
            full_name=obj_in.full_name,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate | dict,
    ) -> User:
        """Update a user, hashing the password if it changed.

        Args:
            db: Async database session.
            db_obj: Existing user instance.
            obj_in: Update data.

        Returns:
            The updated ``User`` instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        else:
            update_data.pop("password", None)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
    ) -> User | None:
        """Authenticate a user by email and password.

        Args:
            db: Async database session.
            email: User email.
            password: Plain-text password to verify.

        Returns:
            The ``User`` if credentials are valid, else ``None``.
        """
        user = await self.get_by_email(db, email=email)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def is_active(user: User) -> bool:
        """Check if the user account is active."""
        return user.is_active

    @staticmethod
    def is_superuser(user: User) -> bool:
        """Check if the user has superuser privileges."""
        return user.is_superuser


# Singleton instance for convenience.
user_crud = CRUDUser(User)
