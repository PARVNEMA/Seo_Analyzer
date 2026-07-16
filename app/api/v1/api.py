"""V1 API router aggregator.

Combines all resource routers into a single ``api_router`` that is
mounted on the FastAPI app under ``/api/v1``.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import seo, crawler, ws, chat

api_router = APIRouter()

api_router.include_router(seo.router, prefix="/seo", tags=["seo"])
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(ws.router, tags=["websockets"])

