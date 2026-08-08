"""
Health Router - Comprehensive system health checks
"""
import logging
import time
from datetime import datetime, timezone
from fastapi import APIRouter
from sqlalchemy import text

from app.core.schemas import HealthResponse
from app.core.config import settings
from app.database.session import engine
from app.services.llm.factory import LLMFactory
from app.services.monitoring import metrics
from app.services.cache_service import cache_service

logger = logging.getLogger("ai_workforce.routers.health")

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

_start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check system health status for all components."""
    services = {}
    overall = "healthy"

    # API
    services["api"] = "healthy"

    # Database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        services["database"] = "healthy"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        services["database"] = f"unhealthy: {str(e)[:100]}"
        overall = "degraded"

    # LLM Providers
    available_llms = LLMFactory.list_available()
    if available_llms:
        services["llm_providers"] = f"healthy ({len(available_llms)} available)"
    else:
        services["llm_providers"] = "unhealthy: no providers configured"
        overall = "degraded"

    # Cache (Redis)
    try:
        if cache_service._use_redis:
            services["cache"] = "healthy (redis)"
        else:
            services["cache"] = "healthy (in-memory fallback)"
    except Exception as e:
        services["cache"] = f"unhealthy: {str(e)[:100]}"

    # Director AI
    if settings.DIRECTOR_AI_ENABLED:
        try:
            from app.agents.director_ai.memory_loader import DirectorMemoryLoader
            loader = DirectorMemoryLoader()
            services["director_ai"] = "healthy"
        except Exception as e:
            services["director_ai"] = f"unhealthy: {str(e)[:100]}"

    # Uptime
    uptime = time.time() - _start_time
    services["uptime_seconds"] = f"{uptime:.0f}"

    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        services=services,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/ready")
async def readiness_check():
    """Check if the system is ready to accept requests."""
    # Check critical dependencies
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ready = True
    except Exception:
        db_ready = False

    llm_ready = len(LLMFactory.list_available()) > 0

    ready = db_ready and llm_ready

    return {
        "ready": ready,
        "database": "ready" if db_ready else "not_ready",
        "llm_providers": "ready" if llm_ready else "not_ready",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/metrics")
async def prometheus_metrics():
    """Export Prometheus metrics."""
    from fastapi.responses import Response
    return Response(
        content=metrics.get_prometheus_metrics(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
