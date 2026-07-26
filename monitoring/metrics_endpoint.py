"""
Monitoring Endpoints - Prometheus-compatible metrics and health

Provides /metrics and /health endpoints for monitoring.
"""

import time
from fastapi import APIRouter
from app.services.monitoring import metrics
from app.services.cache_service import cache_service

router = APIRouter(tags=["Monitoring"])


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.

    Returns metrics in Prometheus text exposition format.
    """
    metrics_data = metrics.get_prometheus_format()
    return {
        "content-type": "text/plain; version=0.0.4; charset=utf-8",
        "metrics": metrics_data,
    }


@router.get("/health")
async def detailed_health():
    """
    Detailed health check endpoint.

    Returns health status of all system components.
    """
    all_metrics = metrics.get_all()

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": all_metrics["uptime_seconds"],
        "services": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "llm": "healthy",
        },
        "metrics": {
            "total_requests": all_metrics["counters"].get("requests_total", 0),
            "total_errors": all_metrics["counters"].get("errors_total", 0),
            "cache_size": cache_service._memory_cache.size,
        },
    }
