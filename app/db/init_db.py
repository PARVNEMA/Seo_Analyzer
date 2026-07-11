"""Database initialization and seeding.

Creates the first superuser account if it does not already exist.
Called during application startup.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.crud.user import user_crud
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


async def create_first_superuser(db: AsyncSession) -> None:
    """Create the initial superuser defined in settings.

    This is idempotent — if the user already exists the function
    returns without making changes.
    """
    settings = get_settings()
    existing = await user_crud.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if existing:
        logger.info("Superuser already exists: %s", settings.FIRST_SUPERUSER_EMAIL)
        return

    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER_EMAIL,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        full_name="Admin",
    )
    user = await user_crud.create(db, obj_in=user_in)
    # Manually set is_superuser since UserCreate doesn't include it
    user.is_superuser = True
    db.add(user)
    await db.commit()
    logger.info("Created first superuser: %s", settings.FIRST_SUPERUSER_EMAIL)


async def init_db(db: AsyncSession) -> None:
    """Run all database initialization tasks.

    Currently only creates the first superuser. Extend this function
    to add more seed data as needed.
    """
    await create_first_superuser(db)
