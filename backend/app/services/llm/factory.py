"""
LLM Factory - Unified interface for creating LLM clients.
Supports OpenAI, Gemini, and DeepSeek providers.
"""
import logging
from typing import Any, Dict, Optional
from .openai import OpenAIClient
from .gemini import GeminiClient
from .deepseek import DeepSeekClient

logger = logging.getLogger("ai_workforce.llm.factory")


class LLMFactory:
    """Factory for creating LLM Client instances."""

    _instances: Dict[str, Any] = {}

    @classmethod
    def get(cls, provider: str):
        """
        Get an LLM client instance for the specified provider.
        Uses singleton pattern to reuse instances.

        Args:
            provider: Provider name (openai, gemini, deepseek)

        Returns:
            LLM client instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()
        providers = {
            "openai": OpenAIClient,
            "gemini": GeminiClient,
            "deepseek": DeepSeekClient,
        }
        if provider not in providers:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Available: {', '.join(providers.keys())}"
            )
        if provider not in cls._instances:
            cls._instances[provider] = providers[provider]()
            logger.info(f"Created LLM client for provider: {provider}")
        return cls._instances[provider]

    @classmethod
    def clear_cache(cls):
        """Clear cached LLM client instances."""
        cls._instances.clear()
        logger.info("LLM client cache cleared")
