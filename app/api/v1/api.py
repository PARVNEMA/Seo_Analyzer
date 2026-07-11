"""V1 API router aggregator.

Combines all resource routers into a single ``api_router`` that is
mounted on the FastAPI app under ``/api/v1``.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import seo

api_router = APIRouter()

api_router.include_router(seo.router, prefix="/seo", tags=["seo"])
