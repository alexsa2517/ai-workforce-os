"""
Monitoring Service - Application metrics and health monitoring

Provides metrics collection, Prometheus-style endpoints,
and application health reporting.
"""

import logging
import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("ai_workforce.monitoring")


class MetricsCollector:
    """
    Thread-safe metrics collector for application monitoring.

    Tracks:
    - Request counts and latencies
    - Error rates
    - LLM usage statistics
    - Agent status
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = {}
        self._start_time = time.time()

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        with self._lock:
            self._gauges[name] = value

    def observe(self, name: str, value: float) -> None:
        """Observe a histogram metric."""
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = []
            self._histograms[name].append(value)

    def get_all(self) -> Dict[str, Any]:
        """Get all metrics."""
        with self._lock:
            uptime = time.time() - self._start_time
            return {
                "uptime_seconds": round(uptime, 2),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values) if values else 0,
                    }
                    for name, values in self._histograms.items()
                },
            }

    def get_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format."""
        with self._lock:
            lines = []
            lines.append(f"# TYPE uptime_seconds gauge")
            lines.append(f"uptime_seconds {time.time() - self._start_time:.2f}")
            lines.append("")

            for name, value in self._counters.items():
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")
            lines.append("")

            for name, value in self._gauges.items():
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {value}")
            lines.append("")

            for name, values in self._histograms.items():
                if values:
                    lines.append(f"# TYPE {name} histogram")
                    lines.append(f"{name}_count {len(values)}")
                    lines.append(f"{name}_sum {sum(values):.4f}")
            lines.append("")

            return "\n".join(lines)

    # Predefined metric helpers

    def track_request(self, method: str, path: str, status: int, duration: float) -> None:
        """Track an API request."""
        self.increment(f"requests_total")
        self.increment(f"requests_{method}_{path.replace('/', '_').strip('_')}")
        self.observe(f"request_duration_seconds", duration)
        if status >= 400:
            self.increment(f"errors_total")

    def track_llm_call(self, provider: str, tokens_used: int, duration: float) -> None:
        """Track an LLM API call."""
        self.increment(f"llm_calls_{provider}")
        self.increment(f"llm_tokens_{provider}", tokens_used)
        self.observe(f"llm_latency_{provider}", duration)


# Global metrics instance
metrics = MetricsCollector()
