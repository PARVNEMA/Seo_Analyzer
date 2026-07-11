"""V1 API router aggregator.

Combines all resource routers into a single ``api_router`` that is
mounted on the FastAPI app under ``/api/v1``.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
