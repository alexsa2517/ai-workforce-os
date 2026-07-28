"""
Monitoring Endpoints - Prometheus-compatible metrics and health
Provides /metrics and /health endpoints for monitoring.
"""
import time
from fastapi import APIRouter
from app.services.cache_service import cache_service
from app.services.monitoring import metrics
from app.core.config import settings

router = APIRouter(tags=["Monitoring"])


@router.get("/api/v1/metrics")
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.
    Returns metrics in text format for Prometheus scraping.
    """
    metrics_data = metrics.get_prometheus_format()
    return {
        "content-type": "text/plain; version=0.0.4; charset=utf-8",
        "metrics": metrics_data,
    }


@router.get("/api/v1/system-status")
async def detailed_health():
    """
    Detailed system health check endpoint.
    Returns health status of all system components.
    """
    all_metrics = metrics.get_all()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "timestamp": time.time(),
        "uptime_seconds": all_metrics["uptime_seconds"],
        "services": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "llm": "healthy",
            "director_ai": "healthy" if settings.DIRECTOR_AI_ENABLED else "disabled",
        },
        "metrics": {
            "total_requests": all_metrics["counters"].get("requests_total", 0),
            "total_errors": all_metrics["counters"].get("errors_total", 0),
            "cache_size": cache_service._memory_cache.size,
            "cache_max_size": cache_service._memory_cache._max_size,
        },
    }
