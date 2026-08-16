"""Unified factory for AI Money Lab and existing agents."""
import logging
from typing import Any, Dict

logger = logging.getLogger("ai_workforce.llm.factory")

class LLMFactory:
    _instances: Dict[str, Any] = {}

    @classmethod
    def get(cls, provider: str):
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
                elif provider == "kimi":
                    from .kimi import KimiClient
                    cls._instances[provider] = KimiClient()
                elif provider in ("claude", "anthropic"):
                    from .claude import ClaudeClient
                    cls._instances[provider] = ClaudeClient()
                else:
                    raise ValueError(f"Unsupported LLM provider: {provider}")
                logger.info("Created LLM client for %s", provider)
            except Exception as exc:
                logger.error("Failed to load LLM provider '%s': %s", provider, exc)
                raise RuntimeError(f"LLM provider '{provider}' is not available: {exc}") from exc
        return cls._instances[provider]

    @classmethod
    def clear_cache(cls):
        cls._instances.clear()
