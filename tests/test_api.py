"""
API Integration Tests
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "AI Workforce OS"


@pytest.mark.asyncio
async def test_chat_without_api_key(client):
    response = await client.post("/api/v1/chat/", json={
        "message": "Hello",
        "provider": "openai"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_providers(client):
    response = await client.get("/api/v1/chat/providers")
    assert response.status_code == 200
    assert "providers" in response.json()
