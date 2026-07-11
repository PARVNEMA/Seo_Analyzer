import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint returns a welcome message."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "Welcome to FastAPI Template" in response.json()["message"]

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"] in ["connected", "disconnected"]
    assert "version" in data
