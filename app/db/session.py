import os
import asyncio
import httpx
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[None, None]:
    """
    Dummy dependency for backwards compatibility.
    Supabase handles connections via HTTP, so a session generator is not needed.
    """
    yield None

async def check_db_connection() -> bool:
    """Ping Supabase REST endpoint to verify API and credentials work."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        logger.error("SUPABASE_URL or SUPABASE_KEY environment variables not set")
        return False
    try:
        async with httpx.AsyncClient() as client:
            headers = {"apikey": key, "Authorization": f"Bearer {key}"}
            # The root of the rest endpoint returns OpenAPI schema info if authenticated
            response = await client.get(f"{url}/rest/v1/", headers=headers)
            return response.status_code == 200
    except Exception as exc:
        logger.error("Supabase connection check failed: %s", exc)
        return False

async def connect_with_retry(max_retries: int = 3, base_delay: float = 1.0) -> None:
    """Verify Supabase connectivity with exponential backoff."""
    for attempt in range(1, max_retries + 1):
        try:
            connected = await check_db_connection()
            if connected:
                logger.info("Supabase connection established (attempt %d)", attempt)
                return
            else:
                raise ValueError("Could not reach Supabase REST API or invalid credentials")
        except Exception as exc:
            if attempt == max_retries:
                logger.error("Failed to connect to Supabase after %d attempts: %s", max_retries, exc)
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning("Supabase connection attempt %d/%d failed, retrying in %.1fs: %s", attempt, max_retries, delay, exc)
            await asyncio.sleep(delay)

async def dispose_engine() -> None:
    """No-op for Supabase as it uses HTTP connections rather than persistent socket pools."""
    pass
