"""
Cache Service - Redis-backed with in-memory fallback
Provides caching for API responses, LLM outputs, and agent states.
"""
import logging
import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger("ai_workforce.cache")


class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if datetime.now() > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if len(self._store) >= self._max_size:
            self._evict_oldest()
        self._store[key] = {
            "value": value,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl or self._default_ttl),
        }

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def _evict_oldest(self) -> None:
        if self._store:
            oldest = min(self._store, key=lambda k: self._store[k]["created_at"])
            del self._store[oldest]


class RedisCache:
    """Redis-backed async cache."""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._default_ttl = 3600

    async def connect(self):
        try:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info("Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self._redis = None

    async def get(self, key: str) -> Optional[Any]:
        if not self._redis:
            return None
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self._redis:
            return
        try:
            await self._redis.setex(
                key,
                ttl or self._default_ttl,
                json.dumps(value, default=str),
            )
        except Exception as e:
            logger.warning(f"Redis set error: {e}")

    async def delete(self, key: str) -> None:
        if not self._redis:
            return
        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")

    async def close(self):
        if self._redis:
            await self._redis.close()


class CacheService:
    """Unified cache service with Redis primary and in-memory fallback."""

    def __init__(self):
        self._redis = RedisCache()
        self._memory = InMemoryCache()
        self._use_redis = False

    async def initialize(self):
        await self._redis.connect()
        self._use_redis = self._redis._redis is not None

    async def get(self, key: str) -> Optional[Any]:
        if self._use_redis:
            value = await self._redis.get(key)
            if value is not None:
                return value
        return self._memory.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if self._use_redis:
            await self._redis.set(key, value, ttl)
        self._memory.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        if self._use_redis:
            await self._redis.delete(key)
        self._memory.delete(key)

    def generate_key(self, prefix: str, *args) -> str:
        """Generate deterministic cache key."""
        content = ":".join(str(a) for a in args)
        hash_part = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_part}"

    async def close(self):
        await self._redis.close()


# Global instance
cache_service = CacheService()
