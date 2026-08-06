"""
LLM Factory - Unified interface for creating LLM clients.
Supports OpenAI, Gemini, and DeepSeek providers.
Robust version that handles failed provider imports.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ai_workforce.llm.factory")

# Lazy imports to prevent total crash if one provider fails
OpenAIClient = None
GeminiClient = None
DeepSeekClient = None

try:
    from .openai import OpenAIClient as _OpenAIClient
    OpenAIClient = _OpenAIClient
except Exception as e:
    logger.error(f"Failed to load OpenAIClient: {e}")

try:
    from .gemini import GeminiClient as _GeminiClient
    GeminiClient = _GeminiClient
except Exception as e:
    logger.error(f"Failed to load GeminiClient: {e}")

try:
    from .deepseek import DeepSeekClient as _DeepSeekClient
    DeepSeekClient = _DeepSeekClient
except Exception as e:
    logger.error(f"Failed to load DeepSeekClient: {e}")


class LLMFactory:
    """Factory for creating LLM Client instances."""

    _instances: Dict[str, Any] = {}

    @classmethod
    def get(cls, provider: str):
        """
        Get an LLM client instance for the specified provider.
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
            
        client_class = providers[provider]
        
        if client_class is None:
            raise RuntimeError(
                f"LLM provider '{provider}' is not available in this environment "
                f"(failed to load required libraries)."
            )

        if provider not in cls._instances:
            cls._instances[provider] = client_class()
            logger.info(f"Created LLM client for provider: {provider}")
            
        return cls._instances[provider]

    @classmethod
    def clear_cache(cls):
        """Clear cached LLM client instances."""
        cls._instances.clear()
        logger.info("LLM client cache cleared")
