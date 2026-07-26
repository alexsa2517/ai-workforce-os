"""
Cache Service - In-memory and Redis caching layer

Provides caching for API responses, LLM outputs, and agent states.
Falls back to in-memory cache if Redis is not available.
"""

import logging
import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("ai_workforce.cache")


class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value by key."""
        entry = self._store.get(key)
        if entry is None:
            return None
        if datetime.now() > entry["expires_at"]:
            del self._store[key]
            logger.debug(f"Cache expired: {key}")
            return None
        logger.debug(f"Cache hit: {key}")
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a cached value with optional TTL."""
        if len(self._store) >= self._max_size:
            self._evict_oldest()
        self._store[key] = {
            "value": value,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl or self._default_ttl),
        }
        logger.debug(f"Cache set: {key}")

    def delete(self, key: str) -> None:
        """Delete a cached value."""
        self._store.pop(key, None)
        logger.debug(f"Cache delete: {key}")

    def clear(self) -> None:
        """Clear all cached values."""
        self._store.clear()
        logger.info("Cache cleared")

    def _evict_oldest(self) -> None:
        """Evict the oldest entry if cache is full."""
        if not self._store:
            return
        oldest_key = min(self._store, key=lambda k: self._store[k]["created_at"])
        del self._store[oldest_key]

    @property
    def size(self) -> int:
        """Return current cache size."""
        return len(self._store)


class CacheService:
    """
    Cache service with in-memory fallback.

    Usage:
        cache = CacheService()
        cache.set("key", "value")
        value = cache.get("key")
    """

    def __init__(self):
        self._memory_cache = InMemoryCache()
        self._redis = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Try Redis first
        if self._redis:
            try:
                value = self._redis.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # Fallback to in-memory
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        # Try Redis first
        if self._redis:
            try:
                serialized = json.dumps(value)
                self._redis.setex(key, ttl or 3600, serialized)
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        # Fallback to in-memory
        self._memory_cache.set(key, value, ttl)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if self._redis:
            try:
                self._redis.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        self._memory_cache.delete(key)

    def generate_key(self, *args) -> str:
        """Generate a cache key from arguments."""
        raw = "|".join(str(a) for a in args)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


# Global cache instance
cache_service = CacheService()
