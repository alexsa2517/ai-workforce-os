"""
Health Router - System health check endpoints.
"""
import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter
from app.core.schemas import HealthResponse
from app.core.config import settings

logger = logging.getLogger("ai_workforce.routers.health")
router = APIRouter(prefix="/api/v1/health", tags=["Health"])
_start_time = time.time()


def _database_healthy() -> bool:
    try:
        from app.database.session import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        return False


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check system health status."""
    services = {"api": "healthy"}
    services["database"] = "healthy" if _database_healthy() else "unhealthy"

    try:
        from app.services.llm.factory import LLMFactory  # noqa: F401
        services["llm_factory"] = "healthy"
    except Exception as exc:
        services["llm_factory"] = f"unhealthy: {str(exc)[:50]}"

    if settings.DIRECTOR_AI_ENABLED:
        try:
            from app.agents.director_ai.memory_loader import DirectorMemoryLoader  # noqa: F401
            services["director_ai"] = "healthy"
        except Exception as exc:
            services["director_ai"] = f"unhealthy: {str(exc)[:50]}"

    overall = "healthy" if all(v == "healthy" for v in services.values()) else "degraded"
    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        services=services,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/ready")
async def readiness_check():
    """Check whether the application is ready to accept requests."""
    ready = _database_healthy()
    return {
        "ready": ready,
        "uptime_seconds": round(time.time() - _start_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
