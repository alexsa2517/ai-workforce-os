#!/usr/bin/env python3
"""
Fix infrastructure files: Docker, monitoring, services, and remaining components.
"""
import os

PROJECT = "/home/ubuntu/ai-workforce-os"

def write(path: str, content: str):
    full = os.path.join(PROJECT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"  Wrote: {path}")

# ============================================================
# 1. Fix docker-compose.yml
# ============================================================
write("docker-compose.yml", '''version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-workforce-backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY:-}
      - JWT_SECRET=${JWT_SECRET:-dev-secret-change-in-production}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./data/ai_workforce.db}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - APP_DEBUG=${APP_DEBUG:-false}
    volumes:
      - ./data:/app/data
      - ./movies:/app/movies
      - ./logs:/app/logs
      - ./knowledge:/app/knowledge
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/v1/health/').raise_for_status()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - ai-workforce

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ai-workforce-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000/api/v1
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - ai-workforce

  # Optional: PostgreSQL database (uncomment to use instead of SQLite)
  # db:
  #   image: postgres:16
  #   container_name: ai-workforce-db
  #   environment:
  #     POSTGRES_DB: ai_workforce
  #     POSTGRES_USER: ai_workforce
  #     POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
  #   volumes:
  #     - pg_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"
  #   restart: unless-stopped
  #   networks:
  #     - ai-workforce

  # Optional: Prometheus monitoring
  # prometheus:
  #   image: prom/prometheus:latest
  #   container_name: ai-workforce-prometheus
  #   volumes:
  #     - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  #   ports:
  #     - "9090:9090"
  #   restart: unless-stopped
  #   networks:
  #     - ai-workforce

networks:
  ai-workforce:
    driver: bridge

# volumes:
#   pg_data:
''')

# ============================================================
# 2. Fix frontend Dockerfile
# ============================================================
write("frontend/Dockerfile", '''# Frontend - Multi-stage build
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files first for caching
COPY package.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
''')

# ============================================================
# 3. Fix frontend nginx.conf
# ============================================================
write("frontend/nginx.conf", '''server {
    listen 3000;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets caching
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
''')

# ============================================================
# 4. Fix services/llm/__init__.py
# ============================================================
write("backend/app/services/llm/__init__.py", '''"""
LLM Services - Language Model provider integrations
Supports OpenAI, Google Gemini, and DeepSeek.
"""
from .factory import LLMFactory
from .openai import OpenAIClient
from .gemini import GeminiClient
from .deepseek import DeepSeekClient

__all__ = ["LLMFactory", "OpenAIClient", "GeminiClient", "DeepSeekClient"]
''')

# ============================================================
# 5. Fix services/__init__.py
# ============================================================
write("backend/app/services/__init__.py", '''"""
Services package - Core application services.
"""
''')

# ============================================================
# 6. Fix auth/__init__.py
# ============================================================
write("backend/app/auth/__init__.py", '''"""
Authentication package - JWT-based authentication utilities.
"""
''')

# ============================================================
# 7. Fix routers/__init__.py
# ============================================================
write("backend/app/routers/__init__.py", '''"""
Routers package - API endpoint modules.
"""
''')

# ============================================================
# 8. Fix monitoring service
# ============================================================
write("monitoring/monitoring_service.py", '''"""
Monitoring Service - System metrics collection and aggregation
Tracks request counts, error rates, response times, and cache stats.
"""
import time
import threading
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class Metrics:
    """System metrics data structure."""
    counters: Dict[str, int] = field(default_factory=dict)
    gauges: Dict[str, float] = field(default_factory=dict)
    histograms: Dict[str, list] = field(default_factory=dict)
    _start_time: float = field(default_factory=time.time)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def increment_counter(self, name: str, value: int = 1):
        with self._lock:
            self.counters[name] = self.counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float):
        with self._lock:
            self.gauges[name] = value

    def observe_histogram(self, name: str, value: float):
        with self._lock:
            if name not in self.histograms:
                self.histograms[name] = []
            self.histograms[name].append(value)

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "avg": sum(v) / len(v) if v else 0,
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self.histograms.items()
                },
                "uptime_seconds": round(time.time() - self._start_time, 2),
            }

    def get_prometheus_format(self) -> str:
        """Return metrics in Prometheus text format."""
        lines = []
        all_metrics = self.get_all()

        for name, value in all_metrics["counters"].items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")

        for name, value in all_metrics["gauges"].items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")

        for name, stats in all_metrics["histograms"].items():
            lines.append(f"# TYPE {name}_total counter")
            lines.append(f"{name}_total {stats['sum']}")
            lines.append(f"# TYPE {name}_count counter")
            lines.append(f"{name}_count {stats['count']}")

        return "\\n".join(lines) + "\\n"


# Global metrics instance
metrics = Metrics()
''')

# ============================================================
# 9. Fix monitoring/prometheus.yml
# ============================================================
write("monitoring/prometheus.yml", '''global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ai-workforce-os'
    scrape_interval: 10s
    metrics_path: /api/v1/metrics
    static_configs:
      - targets: ['backend:8000']
        labels:
          instance: 'ai-workforce-backend'
          environment: 'production'
''')

# ============================================================
# 10. Fix brain/__init__.py and core brain file
# ============================================================
write("brain/brain_service.py", '''"""
Brain Service - Core reasoning and decision-making engine
Coordinates between LLM providers and application logic.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ai_workforce.brain")


class BrainService:
    """Central reasoning engine for AI Workforce OS."""

    def __init__(self):
        self.providers = {}

    def register_provider(self, name: str, provider: Any):
        """Register an LLM provider."""
        self.providers[name] = provider
        logger.info(f"Registered provider: {name}")

    async def reason(
        self,
        query: str,
        provider: str = "openai",
        context: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate a reasoned response using the specified provider.

        Args:
            query: User query
            provider: LLM provider name
            context: Optional context for the reasoning
            temperature: Sampling temperature

        Returns:
            Dict with response and metadata
        """
        llm = self.providers.get(provider)
        if not llm:
            return {"error": f"Provider '{provider}' not found", "response": ""}

        system_prompt = "You are an AI assistant for AI Workforce OS. Provide helpful, accurate responses."
        if context:
            system_prompt += f"\\nContext:\\n{context}"

        try:
            result = llm.generate(
                prompt=query,
                temperature=temperature,
                system_prompt=system_prompt,
            )
            return {
                "response": result.get("content", ""),
                "usage": result.get("usage", {}),
                "provider": provider,
            }
        except Exception as e:
            logger.error(f"Brain reasoning error: {e}", exc_info=True)
            return {"error": str(e), "response": ""}

    def get_available_providers(self) -> list:
        """List available providers."""
        return list(self.providers.keys())


# Singleton instance
brain = BrainService()
''')

# ============================================================
# 11. Fix api/__init__.py
# ============================================================
write("api/__init__.py", '''"""
API package - External API integration utilities.
"""
''')

# ============================================================
# 12. Fix scripts/__init__.py
# ============================================================
write("scripts/__init__.py", '''"""
Scripts package - Utility scripts for setup, migration, and deployment.
"""
''')

# ============================================================
# 13. Fix tests/test_api.py - proper async tests
# ============================================================
write("tests/test_api.py", '''"""
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
''')

# ============================================================
# 14. Create setup.py for installation
# ============================================================
write("backend/setup.py", '''"""
AI Workforce OS - Backend package setup
"""
from setuptools import setup, find_packages

setup(
    name="ai-workforce-os",
    version="0.2.0",
    description="AI Workforce OS - AI-powered workforce management system",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.9.0",
        "pydantic-settings>=2.6.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "openai>=1.48.0",
        "google-generativeai>=0.8.0",
        "PyJWT>=2.9.0",
        "passlib[bcrypt]>=1.7.4",
        "requests>=2.32.0",
        "Pillow>=10.0.0",
        "python-multipart>=0.0.9",
        "httpx>=0.27.0",
        "prometheus-client>=0.21.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-workforce=app.main:app",
        ],
    },
)
''')

# ============================================================
# 15. Create Alembic init file
# ============================================================
write("backend/alembic/versions/__init__.py", '''"""Alembic migration versions package."""
''')

# ============================================================
# 16. Fix .env file with defaults
# ============================================================
write(".env", '''# AI Workforce OS - Development Configuration
# ============================================
# LLM Provider API Keys (replace with your own keys)
# ============================================
OPENAI_API_KEY=
GOOGLE_API_KEY=
DEEPSEEK_API_KEY=
DEEPGRAM_API_KEY=

# ============================================
# JWT Authentication
# ============================================
JWT_SECRET=ai-workforce-os-dev-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ============================================
# Application
# ============================================
APP_NAME=AI Workforce OS
APP_VERSION=0.2.0
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# ============================================
# Database
# ============================================
DATABASE_URL=sqlite:///./ai_workforce.db
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# ============================================
# TTS
# ============================================
TTS_PROVIDER=openai
TTS_VOICE=alloy
TTS_MODEL=tts-1
TTS_SPEED=1.0
TTS_LANGUAGE=th

# ============================================
# Lip-Sync
# ============================================
LIP_SYNC_PROVIDER=simulated
LIP_SYNC_RESOLUTION=720p

# ============================================
# Pipeline
# ============================================
MOVIES_DIR=./movies
SCENES_PER_EPISODE=5
MAX_PARALLEL_JOBS=3

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/ai_workforce.log

# ============================================
# CORS
# ============================================
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
CORS_ALLOW_CREDENTIALS=true

# ============================================
# Director AI
# ============================================
DIRECTOR_AI_ENABLED=true
KNOWLEDGE_BASE_PATH=./knowledge/director-ai
''')

# ============================================================
# 17. Create logs directory init
# ============================================================
write("logs/.gitkeep", '')

# ============================================================
# 18. Create data directory init
# ============================================================
write("data/.gitkeep", '')

# ============================================================
# 19. Create movies directory init
# ============================================================
write("movies/.gitkeep", '')

# ============================================================
# 20. Fix .gitignore
# ============================================================
write(".gitignore", '''# Environment
.env
*.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data
data/
*.db
*.sqlite

# Logs
logs/
*.log

# Movies/Generated content
movies/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Node
frontend/node_modules/
frontend/dist/

# Docker
.docker/
''')

print("=" * 60)
print("All infrastructure fixes applied successfully!")
print("=" * 60)
