"""Application configuration using Pydantic Settings.

Loads settings from environment variables and .env file with validation
and type coercion. Uses ``@lru_cache`` so the settings object is created
only once per process.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "FastAPI Template"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["dev", "staging", "prod"] = "dev"
    API_V1_PREFIX: str = "/api/v1"

    # ── Supabase ─────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ── CORS ─────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # ── Trusted Hosts ────────────────────────────────────────────────────
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1"]


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    The ``@lru_cache`` decorator guarantees the ``.env`` file is read and
    the object is constructed only once per process lifetime.
    """
    return Settings()
