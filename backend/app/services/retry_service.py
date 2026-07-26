"""
Retry Service - Retry mechanism with exponential backoff

Provides decorators and utilities for retrying failed operations
with exponential backoff, particularly for LLM API calls.
"""

import logging
import time
import functools
from typing import Callable, TypeVar, Any

logger = logging.getLogger("ai_workforce.retry")

F = TypeVar("F", bound=Callable[..., Any])


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    jitter: bool = True,
) -> Callable[[F], F]:
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exception types to catch and retry
        jitter: Whether to add random jitter to delay

    Returns:
        Decorated function with retry behavior

    Example:
        @retry(max_attempts=3, base_delay=2.0)
        def call_llm(prompt):
            return llm.generate(prompt)
    """
    import random

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.info(f"Function '{func.__name__}' succeeded on attempt {attempt}")
                    return result
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = base_delay * (exponential_base ** (attempt - 1))
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    logger.warning(
                        f"Function '{func.__name__}' failed (attempt {attempt}/{max_attempts}): "
                        f"{e}. Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

            raise last_exception  # Should never reach here

        wrapper.retry_config = {
            "max_attempts": max_attempts,
            "base_delay": base_delay,
        }
        return wrapper  # type: ignore

    return decorator


class CircuitBreaker:
    """
    Simple circuit breaker to prevent cascading failures.

    Usage:
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        result = breaker.call(call_llm, prompt)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._failure_count = 0
        self._last_failure_time: float = 0
        self._state = "closed"  # closed, open, half-open

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self._state == "open":
            if time.time() - self._last_failure_time >= self._recovery_timeout:
                self._state = "half-open"
                logger.info("Circuit breaker: half-open, testing...")
            else:
                raise RuntimeError("Circuit breaker is open - service unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        if self._state == "half-open":
            self._state = "closed"
            self._failure_count = 0
            logger.info("Circuit breaker: closed (recovered)")

    def _on_failure(self):
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self._failure_threshold:
            self._state = "open"
            logger.warning(
                f"Circuit breaker: OPEN (failures={self._failure_count})"
            )

    @property
    def state(self) -> str:
        """Get current circuit breaker state."""
        return self._state

    @property
    def is_available(self) -> bool:
        """Check if the service is available."""
        return self._state != "open"
