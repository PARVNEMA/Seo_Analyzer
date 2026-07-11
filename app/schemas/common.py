"""Common response and utility schemas.

Reusable schemas shared across multiple endpoints.
"""

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Generic message response.

    Attributes:
        message: Human-readable status or confirmation message.
    """

    message: str


class HealthResponse(BaseModel):
    """Health-check endpoint response.

    Attributes:
        status: Overall service status (e.g. ``"healthy"``).
        database: Database connectivity status.
        version: Application version string.
    """

    status: str
    database: str
    version: str


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints.

    Attributes:
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return per page.
    """

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum records per page",
    )
