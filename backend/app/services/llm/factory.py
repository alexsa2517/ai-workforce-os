"""
LLM Factory - Unified interface for creating LLM clients.
Supports OpenAI, Gemini, and DeepSeek providers.
Dynamic loading version to handle restricted environments.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ai_workforce.llm.factory")

class LLMFactory:
    """Factory for creating LLM Client instances with dynamic loading."""

    _instances: Dict[str, Any] = {}

    @classmethod
    def get(cls, provider: str):
        """
        Get an LLM client instance for the specified provider.
        Loads the provider class only when requested.
        """
        provider = provider.lower()
        
        if provider not in cls._instances:
            try:
                if provider == "openai":
                    from .openai import OpenAIClient
                    cls._instances[provider] = OpenAIClient()
                elif provider == "deepseek":
                    from .deepseek import DeepSeekClient
                    cls._instances[provider] = DeepSeekClient()
                elif provider == "gemini":
                    from .gemini import GeminiClient
                    cls._instances[provider] = GeminiClient()
                else:
                    raise ValueError(f"Unsupported LLM provider: {provider}")
                
                logger.info(f"Successfully created LLM client for: {provider}")
            except Exception as e:
                logger.error(f"Failed to load LLM provider '{provider}': {e}")
                raise RuntimeError(f"LLM provider '{provider}' is not available: {e}")
            
        return cls._instances[provider]

    @classmethod
    def clear_cache(cls):
        """Clear cached LLM client instances."""
        cls._instances.clear()
        logger.info("LLM client cache cleared")
