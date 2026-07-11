import pytest
from httpx import AsyncClient
from app.core.config import get_settings

settings = get_settings()
PREFIX = settings.API_V1_PREFIX

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login returns tokens."""
    response = await client.post(
        f"{PREFIX}/auth/login",
        data={"username": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    """Test login with wrong password."""
    response = await client.post(
        f"{PREFIX}/auth/login",
        data={"username": "user@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with nonexistent email."""
    response = await client.post(
        f"{PREFIX}/auth/login",
        data={"username": "nobody@example.com", "password": "password123"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient, test_user):
    """Test refreshing an access token using a refresh token."""
    # First login to get a refresh token
    login_resp = await client.post(
        f"{PREFIX}/auth/login",
        data={"username": "user@example.com", "password": "password123"}
    )
    refresh_token = login_resp.json()["refresh_token"]
    
    # Now use refresh token
    refresh_resp = await client.post(
        f"{PREFIX}/auth/refresh?refresh_token={refresh_token}",
    )
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
