"""Common utility functions.

Small helpers used throughout the application.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import Query


def generate_uuid() -> uuid.UUID:
    """Generate a new UUID4."""
    return uuid.uuid4()


def utc_now() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def paginate_params(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records per page"),
) -> dict[str, int]:
    """FastAPI dependency that extracts pagination query parameters.

    Usage::

        @router.get("/items")
        async def list_items(pagination: dict = Depends(paginate_params)):
            skip, limit = pagination["skip"], pagination["limit"]
    """
    return {"skip": skip, "limit": limit}
