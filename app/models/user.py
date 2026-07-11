"""User SQLAlchemy model.

Defines the User table with UUID primary key, authentication fields,
and role flags. Inherits timestamp columns from TimestampMixin.
"""

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    """User database model.

    Attributes:
        id: Unique identifier (UUID4).
        email: Unique email address, indexed for fast lookup.
        hashed_password: Bcrypt-hashed password string.
        full_name: Optional display name.
        is_active: Whether the user account is active.
        is_superuser: Whether the user has admin privileges.
        created_at: Timestamp of record creation (from TimestampMixin).
        updated_at: Timestamp of last update (from TimestampMixin).
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, email={self.email!r})>"
