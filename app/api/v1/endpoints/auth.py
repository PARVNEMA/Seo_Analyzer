"""Authentication endpoints.

Provides login and token refresh routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import auth_controller
from app.db.session import get_db
from app.schemas.auth import Token

router = APIRouter()


@router.post("/login", response_model=Token, summary="Login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Authenticate with email and password.

    Uses OAuth2 password flow. The ``username`` field should contain
    the user's email address.
    """
    return await auth_controller.login(
        db,
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/refresh", response_model=Token, summary="Refresh token")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Exchange a valid refresh token for a new token pair."""
    return await auth_controller.refresh_token(db, token=refresh_token)
