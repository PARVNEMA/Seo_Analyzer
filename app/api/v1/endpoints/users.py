"""User management endpoints.

Provides CRUD routes for users. Most operations require superuser
access; regular users can only view and update their own profile.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.user_controller import user_controller
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user, get_current_superuser
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user


@router.put("/me", response_model=UserResponse, summary="Update current user")
async def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update the currently authenticated user's profile."""
    return await user_controller.update_user(db, user_id=current_user.id, user_in=user_in)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users",
    dependencies=[Depends(get_current_superuser)],
)
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> UserListResponse:
    """Return a paginated list of all users (superuser only)."""
    return await user_controller.get_users(db, skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    dependencies=[Depends(get_current_superuser)],
)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Fetch a single user by ID (superuser only)."""
    return await user_controller.get_user(db, user_id=user_id)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Create user",
    dependencies=[Depends(get_current_superuser)],
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Create a new user (superuser only)."""
    return await user_controller.create_user(db, user_in=user_in)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user by ID",
    dependencies=[Depends(get_current_superuser)],
)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update a user by ID (superuser only)."""
    return await user_controller.update_user(db, user_id=user_id, user_in=user_in)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete a user by ID (superuser only)."""
    await user_controller.delete_user(db, user_id=user_id)
    return MessageResponse(message=f"User {user_id} deleted successfully")
