import pytest
from datetime import timedelta
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.config import get_settings

settings = get_settings()

def test_password_hashing():
    """Test password hashing and verification."""
    password = "supersecretpassword"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_access_token_creation_and_verification():
    """Test JWT creation and decoding."""
    subject = "user123"
    token = create_access_token(subject=subject, expires_delta=timedelta(minutes=15))
    
    payload = verify_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "access"
    assert "exp" in payload

def test_refresh_token_creation():
    """Test refresh token creation."""
    subject = "user123"
    token = create_refresh_token(subject=subject)
    
    payload = verify_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "refresh"

def test_expired_token():
    """Test decoding an expired token raises an exception."""
    from jose import JWTError
    
    # Create an expired token by setting negative expiry
    token = create_access_token(subject="test", expires_delta=timedelta(minutes=-1))
    
    with pytest.raises(JWTError):
        verify_token(token)
