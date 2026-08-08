"""
Monitoring Service - Prometheus metrics and health tracking
"""
import logging
import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from app.core.config import settings

logger = logging.getLogger("ai_workforce.monitoring")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "aiworkforce_requests_total",
    "Total requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "aiworkforce_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

LLM_REQUESTS = Counter(
    "aiworkforce_llm_requests_total",
    "LLM requests by provider",
    ["provider", "model", "status"],
)

LLM_TOKENS = Counter(
    "aiworkforce_llm_tokens_total",
    "Total tokens used",
    ["provider", "model", "type"],
)

LLM_COST = Counter(
    "aiworkforce_llm_cost_usd_total",
    "Total LLM cost in USD",
    ["provider", "model"],
)

LLM_DURATION = Histogram(
    "aiworkforce_llm_duration_seconds",
    "LLM request duration",
    ["provider"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
)

AGENT_COUNT = Gauge(
    "aiworkforce_agents_total",
    "Number of registered agents",
    ["status"],
)

TASK_COUNT = Gauge(
    "aiworkforce_tasks_total",
    "Number of tasks by status",
    ["status"],
)

APP_INFO = Info("aiworkforce_app", "Application information")


class MetricsCollector:
    """Metrics collector with Prometheus export."""

    def __init__(self):
        self._start_time = time.time()
        APP_INFO.info({"version": settings.APP_VERSION, "name": settings.APP_NAME})

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics."""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def record_llm_request(
        self,
        provider: str,
        model: str,
        status: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        duration: float,
    ):
        """Record LLM usage metrics."""
        LLM_REQUESTS.labels(provider=provider, model=model, status=status).inc()
        LLM_TOKENS.labels(provider=provider, model=model, type="prompt").inc(prompt_tokens)
        LLM_TOKENS.labels(provider=provider, model=model, type="completion").inc(completion_tokens)
        LLM_COST.labels(provider=provider, model=model).inc(cost_usd)
        LLM_DURATION.labels(provider=provider).observe(duration)

    def set_agent_count(self, status: str, count: int):
        """Set agent count gauge."""
        AGENT_COUNT.labels(status=status).set(count)

    def set_task_count(self, status: str, count: int):
        """Set task count gauge."""
        TASK_COUNT.labels(status=status).set(count)

    def get_prometheus_metrics(self) -> bytes:
        """Export metrics in Prometheus format."""
        return generate_latest()

    def get_uptime_seconds(self) -> float:
        """Get application uptime."""
        return time.time() - self._start_time


# Global instance
metrics = MetricsCollector()
