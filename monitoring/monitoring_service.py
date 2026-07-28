"""
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

        return "\n".join(lines) + "\n"


# Global metrics instance
metrics = Metrics()
