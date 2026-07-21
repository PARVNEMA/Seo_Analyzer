"""Application configuration using Pydantic Settings.

Loads settings from environment variables and .env file with validation
and type coercion. Uses ``@lru_cache`` so the settings object is created
only once per process.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal
from dotenv import load_dotenv

# Load env variables into os.environ so LangChain and other libraries can access them
load_dotenv()

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

    # ── AI Providers ─────────────────────────────────────────────────────
    LLM_PROVIDER: str = "groq"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    MAX_CRAWL_PAGES: int = 20

    # ── Supabase ─────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_PUBLISHABLE_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""

    # ── CORS ─────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173","https://ai-seo-frontend-flax.vercel.app"]

    # ── Trusted Hosts ────────────────────────────────────────────────────
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1"]



    @property
    def SUPABASE_KEY(self) -> str:
        """Returns the secret key (service role) if available, otherwise publishable key."""
        return self.SUPABASE_SECRET_KEY or self.SUPABASE_PUBLISHABLE_KEY


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    The ``@lru_cache`` decorator guarantees the ``.env`` file is read and
    the object is constructed only once per process lifetime.
    """
    return Settings()
