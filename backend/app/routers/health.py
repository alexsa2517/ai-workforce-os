"""
Health Router - System health check endpoints
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.core.schemas import HealthResponse

logger = logging.getLogger("ai_workforce.routers.health")

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check system health status."""
    services = {
        "api": "healthy",
        "llm_factory": "healthy",
    }
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services=services,
        timestamp=datetime.utcnow(),
    )


@router.get("/ready")
async def readiness_check():
    """Check if the system is ready to accept requests."""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
    }
