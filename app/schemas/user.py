"""User Pydantic schemas.

Defines request/response models for user-related API operations.
All schemas use Pydantic v2 conventions.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema with shared user fields.

    Attributes:
        email: Valid email address.
        full_name: Optional display name.
    """

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user.

    Attributes:
        password: Plain-text password (will be hashed before storage).
    """

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating an existing user.

    All fields are optional so callers can send partial updates.

    Attributes:
        email: New email address.
        full_name: New display name.
        password: New plain-text password.
        is_active: Account active flag.
    """

    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(None, min_length=8, max_length=128)
    is_active: bool | None = None


class UserResponse(UserBase):
    """Schema returned to clients for a single user.

    Attributes:
        id: User UUID.
        is_active: Whether the account is active.
        is_superuser: Whether the user has admin privileges.
        created_at: Record creation timestamp.
        updated_at: Record last-update timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Paginated list response for users.

    Attributes:
        items: List of user records for the current page.
        total: Total number of users matching the query.
    """

    items: list[UserResponse]
    total: int
