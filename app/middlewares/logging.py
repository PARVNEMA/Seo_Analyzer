"""Request logging middleware.

Logs every incoming request with its method, path, status code, and
duration. Attaches a unique ``request_id`` to each request for
traceability.
"""

from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs request details and injects a request ID."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Bind request_id to structlog context for this request.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Attach request_id to request state for access in route handlers.
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_error",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                request_id=request_id,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add request_id header to response for client-side tracing.
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            request_id=request_id,
        )

        return response
