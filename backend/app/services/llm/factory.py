"""
LLM Factory with Fallback Chain and Retry Logic
Automatically retries failed requests and falls back to alternative providers.
"""
import logging
import time
from typing import Any, Dict, Optional, AsyncGenerator, List
from tenacity import (
    retry, stop_after_attempt, wait_exponential_jitter,
    retry_if_exception_type, before_sleep_log
)
from openai import APITimeoutError, APIError, AuthenticationError

from app.core.config import settings
from .openai import OpenAIClient
from .deepseek import DeepSeekClient
from .gemini import GeminiClient

logger = logging.getLogger("ai_workforce.llm.factory")

# Exception types that trigger retry
RETRY_EXCEPTIONS = (APITimeoutError, APIError, ConnectionError, TimeoutError)


class LLMFactory:
    """Factory for creating LLM clients with automatic fallback."""

    _clients = {
        "openai": None,
        "deepseek": None,
        "gemini": None,
    }

    @classmethod
    def _get_client(cls, provider: str):
        """Get or create LLM client (singleton pattern)."""
        provider = provider.lower()

        if cls._clients[provider] is None:
            if provider == "openai":
                cls._clients[provider] = OpenAIClient()
            elif provider == "deepseek":
                cls._clients[provider] = DeepSeekClient()
            elif provider == "gemini":
                cls._clients[provider] = GeminiClient()
            else:
                raise ValueError(f"Unknown provider: {provider}")

        return cls._clients[provider]

    @classmethod
    def get(cls, provider: str):
        """Get LLM client by name."""
        return cls._get_client(provider)

    @classmethod
    def list_available(cls) -> List[str]:
        """List available (configured) providers."""
        available = []
        for name in ["openai", "deepseek", "gemini"]:
            client = cls._get_client(name)
            if client.is_available:
                available.append(name)
        return available

    @classmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type(RETRY_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def generate(
        cls,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
        fallback_order: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate with automatic fallback.

        1. Try primary provider with retry
        2. If all retries exhausted, try next provider in fallback_order
        3. Return error only if all providers fail
        """
        fallback_order = fallback_order or settings.LLM_FALLBACK_ORDER
        primary = provider or fallback_order[0]

        last_error = None

        for prov in [primary] + [p for p in fallback_order if p != primary]:
            try:
                client = cls._get_client(prov)

                if not client.is_available:
                    logger.warning(f"Provider {prov} not available (no API key)")
                    continue

                start_time = time.time()
                result = await client.generate(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                )

                duration = time.time() - start_time

                # Check if client returned error dict
                if result.get("error"):
                    logger.warning(f"Provider {prov} returned error: {result['error']}")
                    last_error = result
                    continue

                result["_provider_used"] = prov
                result["_duration_seconds"] = round(duration, 3)
                result["_fallback_used"] = prov != primary

                logger.info(
                    f"LLM success: provider={prov}, model={result.get('model')}, "
                    f"tokens={result.get('usage', {}).get('total_tokens', 0)}, "
                    f"duration={duration:.3f}s"
                )

                return result

            except RETRY_EXCEPTIONS as e:
                logger.warning(f"Provider {prov} failed (will retry/fallback): {e}")
                last_error = e
                # If this is the primary provider, let tenacity retry
                if prov == primary:
                    raise
                continue
            except Exception as e:
                logger.error(f"Provider {prov} failed permanently: {e}")
                last_error = e
                continue

        # All providers failed
        logger.error(f"All LLM providers failed. Last error: {last_error}")
        return {
            "content": "",
            "usage": {},
            "error": "all_providers_failed",
            "detail": f"All LLM providers are unavailable. Last error: {str(last_error)}",
            "_provider_used": None,
        }

    @classmethod
    async def generate_stream(
        cls,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from primary provider."""
        prov = provider or settings.LLM_FALLBACK_ORDER[0]
        client = cls._get_client(prov)

        if not client.is_available:
            logger.error(f"Provider {prov} not available for streaming")
            yield ""
            return

        async for chunk in client.generate_stream(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        ):
            yield chunk
