"""V1 API router aggregator.

Combines all resource routers into a single ``api_router`` that is
mounted on the FastAPI app under ``/api/v1``.
"""

from fastapi import APIRouter, Depends

from app.api.v1.endpoints import seo, crawler, ws, chat, auth
from app.dependencies.auth import get_current_user

api_router = APIRouter()

# Public routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ws.router, tags=["websockets"]) # WS has its own protection

# Protected routes
api_router.include_router(seo.router, prefix="/seo", tags=["seo"], dependencies=[Depends(get_current_user)])
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"], dependencies=[Depends(get_current_user)])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])

