"""
API Tests - Comprehensive test suite for all API endpoints.
"""
import pytest
import json
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch


@pytest.fixture
def app():
    """Create test application."""
    from app.main import app
    return app


@pytest.fixture
def mock_llm():
    """Create mock LLM client."""
    mock = MagicMock()
    mock.generate.return_value = {
        "content": "Test response from mock LLM",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }
    return mock


class TestHealthEndpoints:
    """Test health and readiness endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, app):
        """Test health check endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
            assert "version" in data
            assert "services" in data

    @pytest.mark.asyncio
    async def test_readiness_check(self, app):
        """Test readiness endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["ready"] is True
            assert "uptime_seconds" in data


class TestRootEndpoints:
    """Test legacy root endpoints."""

    @pytest.mark.asyncio
    async def test_root(self, app):
        """Test root endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "version" in data

    @pytest.mark.asyncio
    async def test_legacy_health(self, app):
        """Test legacy health endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


class TestAgentsEndpoints:
    """Test agent management endpoints."""

    @pytest.mark.asyncio
    async def test_list_agents(self, app):
        """Test listing all agents."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/agents/")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_agent(self, app):
        """Test getting a specific agent."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/agents/director_ai")
            assert response.status_code == 200
            data = response.json()
            assert data["agent_id"] == "director_ai"
            assert data["name"] == "DirectorAI"

    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self, app):
        """Test getting a non-existent agent."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/agents/nonexistent")
            assert response.status_code == 404


class TestChatEndpoints:
    """Test chat endpoints."""

    @pytest.mark.asyncio
    async def test_list_providers(self, app):
        """Test listing available providers."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/chat/providers")
            assert response.status_code == 200
            data = response.json()
            assert "providers" in data
            assert len(data["providers"]) >= 3


class TestVoiceEndpoints:
    """Test voice/TTS endpoints."""

    @pytest.mark.asyncio
    async def test_list_voices(self, app):
        """Test listing available voices."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/voice/voices")
            assert response.status_code == 200
            data = response.json()
            assert "voices" in data
