"""FastAPI application entry point.

Creates the FastAPI app instance, registers middleware, exception
handlers, and routers, and defines the application lifespan for
startup/shutdown events.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.db.session import check_db_connection, connect_with_retry, dispose_engine
from app.middlewares.logging import RequestLoggingMiddleware
from app.schemas.common import HealthResponse

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan managing startup and shutdown tasks."""
    # ── Startup ──────────────────────────────────────────────────────
    setup_logging()
    logger.info(
        "Starting %s v%s [%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT,
    )

    # Verify database connectivity with retry.
    try:
        await connect_with_retry()
        logger.info("Database connection verified")
    except Exception:
        logger.warning("Could not verify database connection at startup")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    await dispose_engine()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Factory function that builds and configures the FastAPI app."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="A production-ready FastAPI boilerplate template.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware (order matters: outermost first) ───────────────────
    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    if settings.ENVIRONMENT != "dev":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS,
        )

    # ── Exception handlers ───────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ──────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── Health-check endpoints ───────────────────────────────────────
    @app.get("/", tags=["health"], summary="Root")
    async def root() -> dict[str, str]:
        """Root endpoint — confirms the service is running."""
        return {"message": f"Welcome to {settings.APP_NAME}"}

    @app.get("/health", response_model=HealthResponse, tags=["health"], summary="Health check")
    async def health() -> HealthResponse:
        """Health-check endpoint that also pings the database."""
        db_ok = await check_db_connection()
        return HealthResponse(
            status="healthy" if db_ok else "degraded",
            database="connected" if db_ok else "disconnected",
            version=settings.APP_VERSION,
        )

    return app


# Create the app instance used by uvicorn.
app = create_app()
