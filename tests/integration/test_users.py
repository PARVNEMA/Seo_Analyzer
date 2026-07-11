import pytest
from httpx import AsyncClient
from app.core.config import get_settings

settings = get_settings()
PREFIX = settings.API_V1_PREFIX

@pytest.mark.asyncio
async def test_get_current_user(authenticated_client: AsyncClient):
    """Test getting own profile."""
    response = await authenticated_client.get(f"{PREFIX}/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected route without token."""
    response = await client.get(f"{PREFIX}/users/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_users_superuser(superuser_client: AsyncClient, test_user):
    """Test superuser can list users."""
    response = await superuser_client.get(f"{PREFIX}/users/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2  # Superuser and test_user

@pytest.mark.asyncio
async def test_list_users_forbidden(authenticated_client: AsyncClient):
    """Test normal user cannot list users."""
    response = await authenticated_client.get(f"{PREFIX}/users/")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_user_superuser(superuser_client: AsyncClient):
    """Test superuser can create a new user."""
    new_user = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User"
    }
    response = await superuser_client.post(f"{PREFIX}/users/", json=new_user)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == new_user["email"]

@pytest.mark.asyncio
async def test_update_current_user(authenticated_client: AsyncClient):
    """Test user can update their own profile."""
    update_data = {
        "full_name": "Updated Name"
    }
    response = await authenticated_client.put(f"{PREFIX}/users/me", json=update_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"

@pytest.mark.asyncio
async def test_delete_user_superuser(superuser_client: AsyncClient, test_user):
    """Test superuser can delete a user."""
    response = await superuser_client.delete(f"{PREFIX}/users/{test_user.id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
