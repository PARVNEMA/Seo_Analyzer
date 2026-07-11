"""JWT token utilities and password hashing helpers.

Uses ``python-jose`` for JWT encoding / decoding and ``passlib`` with
bcrypt for secure password hashing.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# ── Password hashing ────────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return the bcrypt hash of *password*."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if *plain_password* matches *hashed_password*."""
    return _pwd_context.verify(plain_password, hashed_password)


# ── JWT helpers ──────────────────────────────────────────────────────────────

def _create_token(
    data: dict[str, Any],
    expires_delta: timedelta,
    token_type: str = "access",
) -> str:
    """Create a signed JWT with the given *data* and expiry."""
    now = datetime.now(timezone.utc)
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": now + expires_delta,
            "iat": now,
            "type": token_type,
        }
    )
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a short-lived access token.

    Parameters
    ----------
    subject:
        The token subject, typically a user ID or e-mail.
    expires_delta:
        Custom expiry duration.  Falls back to
        ``ACCESS_TOKEN_EXPIRE_MINUTES`` from settings.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token({"sub": str(subject)}, expires_delta, token_type="access")


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a long-lived refresh token.

    Parameters
    ----------
    subject:
        The token subject, typically a user ID or e-mail.
    expires_delta:
        Custom expiry duration.  Falls back to
        ``REFRESH_TOKEN_EXPIRE_DAYS`` from settings.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token({"sub": str(subject)}, expires_delta, token_type="refresh")


def verify_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT.

    Returns
    -------
    dict
        The decoded payload on success.

    Raises
    ------
    JWTError
        If the token is invalid, expired, or tampered with.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise
